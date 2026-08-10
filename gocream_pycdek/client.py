import datetime as dt
import logging
from copy import deepcopy
from enum import IntEnum
from io import BytesIO
from pathlib import Path
from pathlib import PurePath

import jwt
import requests
from requests import HTTPError
from requests import Response

from gocream_pycdek.exceptions import CdekApiAccessException
from gocream_pycdek.exceptions import CdekApiException
from gocream_pycdek.exceptions import CdekApiUnavailableException
from gocream_pycdek.exceptions import CdekApiWrongTokenTypeException
from gocream_pycdek.exceptions import CdekNoAuthClientException
from gocream_pycdek.exceptions import CdekRequestException
from gocream_pycdek.utils import clear_dict
from gocream_pycdek.utils import drop_none
from gocream_pycdek.utils import get_secure


logger = logging.getLogger("gocream_pycdek")


PRODUCTION_API_URL = "https://api.cdek.ru"
TEST_API_URL = "https://api.edu.cdek.ru"


class ContractType(IntEnum):
    """
    Type of the order, as sent in the `type` field

    Указывается в каждом заказе, а не в клиенте: тип — свойство заказа, а не учётной
    записи. `DELIVERY` доступен любому договору, `ONLINE_STORE` — только договору
    с интернет-магазином, поэтому одна и та же учётная запись может отправлять оба
    типа.

    Attributes:
        ONLINE_STORE: Заказ «интернет-магазин».
        DELIVERY: Заказ «доставка».
    """

    ONLINE_STORE = 1
    DELIVERY = 2


# Webhook Event Types
# docs: https://apidoc.cdek.ru/#tag/common/Opisanie-struktury-vebhukov
WEBHOOK_EVENT_TYPE_ORDER = "ORDER_STATUS"  # событие по статусам
WEBHOOK_EVENT_TYPE_PRINT = "PRINT_FORM"  # готовность печатной формы
WEBHOOK_EVENT_TYPE_PHOTO = "DOWNLOAD_PHOTO"  # получение фото документов по заказам


class CdekClient:
    """
    Client for cdek api

    Клиент держит открытую HTTP-сессию, поэтому у него есть время жизни. Соединение
    переиспользуется между запросами, и это тем выгоднее, чем дольше живёт экземпляр -
    один клиент на приложение предпочтительнее клиента на запрос.

    Освобождать соединения нужно явно, через `close` или блок `with`:

    ```python
    with CdekClient("id", "secret") as client:
        regions = client.get_regions()
    ```

    Без этого сокеты остаются открытыми, пока на клиента есть хоть одна ссылка.
    Сборщик мусора их в итоге доберёт, но предупреждения при этом не будет,
    так что накопление дескрипторов легко не заметить.

    Attributes:
        TOKEN_REFRESH_MARGIN: Насколько раньше срока клиент идёт за новым токеном. Запас
            нужен на расхождение часов с СДЭК и на время запроса, который этим токеном
            уйдёт. СДЭК выдаёт токен на час, так что пять минут стоят примерно 8% срока
            жизни.
        DEFAULT_TIMEOUT: Таймаут запроса как пара `(connect, read)` в секундах. Отдельный
            атрибут, а не литерал в `send`, чтобы значение переопределялось наследником
            или на экземпляре, без правки вызовов.
    """

    RESOURCE_AUTH_TOKEN = "v2/oauth/token"
    RESOURCE_ORDER = "v2/orders"
    RESOURCE_INTAKES = "v2/intakes"
    RESOURCE_REGIONS = "v2/location/regions"
    RESOURCE_CITIES = "v2/location/cities"
    RESOURCE_RECEIPT = "v2/print/orders"
    RESOURCE_BARCODE = "v2/print/barcodes"
    RESOURCE_SUBSCRIPTION = "v2/webhooks"
    RESOURCE_DELIVERYPOINTS = "v2/deliverypoints"
    RESOURCE_CALCULATOR_TARIFF = "v2/calculator/tariff"
    RESOURCE_CALCULATOR_URL = "calculator/calculate_price_by_json.php"

    TOKEN_REFRESH_MARGIN: dt.timedelta = dt.timedelta(minutes=5)
    DEFAULT_TIMEOUT: tuple[float, float] = (3, 7)

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = PRODUCTION_API_URL,
    ) -> None:
        """
        Args:
            client_id: CDEK client ID.
            client_secret: CDEK client secret.
            base_url: Base URL of the CDEK API.
        """

        self.client_id = client_id
        self._client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None
        self._token_expires_at: dt.datetime | None = None

        # Сессия держит TCP-соединение открытым между запросами. На пагинации
        # `get_all_cities` это разница между одним handshake и сотнями.
        self._session = requests.Session()

    def __enter__(self):
        """
        Enter runtime context and return the client itself
        """

        return self

    def __exit__(self, *exc_info):
        """
        Leave runtime context, closing the client and releasing its connections
        """

        self.close()

    def close(self) -> None:
        """
        Close underlying HTTP session and release pooled connections

        Вызывается автоматически при выходе из блока `with`. Клиент после закрытия
        остаётся работоспособным: следующий запрос откроет соединение заново.
        """

        self._session.close()

    @property
    def token(self) -> str:
        """
        request token if needed and return token
        """

        deadline = dt.datetime.now() + self.TOKEN_REFRESH_MARGIN
        is_expired = self._token_expires_at is None or self._token_expires_at <= deadline

        if self._token is None or is_expired:
            # token not getted or expired -> request a new one
            response = self.authorization()
            token: str = response["access_token"]
            token_data = jwt.decode(token, options={"verify_signature": False})

            self._token = token
            self._token_expires_at = dt.datetime.fromtimestamp(token_data["exp"])

        return self._token

    def authorization(self):
        """
        request jwt token for use in api requests
        """

        response = self._session.post(
            self.get_url(self.RESOURCE_AUTH_TOKEN),
            params={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self._client_secret,
            },
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:
            message = response.text
            code = None

            if response.headers["Content-Type"] == "application/json":
                json = response.json()

                if "error_description" in json and "invalid_client" in json:
                    message = json["error_description"]
                    code = json["invalid_client"]

                elif "reason" in json and len(json) == 1:
                    message = json["reason"]

            if code == "invalid_client" and message == "Bad client credentials":
                raise CdekApiAccessException()

            elif code is None and message == "Service Unavailable":
                raise CdekApiUnavailableException()

            raise CdekApiException(message, code)

        else:
            json = response.json()

        if json["token_type"] != "bearer":
            raise CdekApiWrongTokenTypeException(json["token_type"])

        return json

    def get_url(self, resource):
        """
        make request url
        """

        resource = resource.as_posix() if isinstance(resource, PurePath) else str(resource)
        if resource.startswith(("http://", "https://")):
            return resource

        return f"{self.base_url}/{resource.lstrip('/')}"

    def get_headers(self):
        """
        make headers for requests
        """

        return {"Authorization": f"Bearer {self.token}"}

    def send(self, resource, method, *, data=None, params=None, raise_errors=True, **kwargs):
        """
        Send authorized request to the API

        Args:
            resource (str|PurePath): Resource path or an absolute url.
            method (str): HTTP method, e.g. `get`, `post` or `delete`.
            data (dict, optional): Request body, sent as json. Defaults to None.
            params (dict, optional): Query string parameters. Defaults to None.
            raise_errors (bool, optional): Raise `CdekRequestException` on error status.
                Defaults to True.
            **kwargs: Passed to `requests.Session.request` as is. Свой `headers` заменяет
                набор целиком, а не дополняет его: так подменяется `Authorization` или
                отправляется анонимный запрос, если передать `headers={}`.

        Returns:
            Response: Response as returned by `requests`.

        Raises:
            CdekRequestException: Ответ с ошибочным статусом при `raise_errors=True`.
        """

        # Не `setdefault`: его аргумент вычисляется всегда, поэтому анонимный запрос всё
        # равно успевал сходить за токеном. Здесь `get_headers` зовётся, только если своих
        # заголовков не передали.
        headers = kwargs.pop("headers", None)
        if headers is None:
            headers = self.get_headers()

        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)

        url = self.get_url(resource)
        response = self._session.request(method, url, json=data, params=params, headers=headers, **kwargs)

        logger.debug("%s %s responded %s", method.upper(), url, response.status_code)

        if raise_errors:
            try:
                response.raise_for_status()

            except HTTPError as error:
                raise CdekRequestException(str(error), response=response) from error

        return response

    def registrate_order(
        self,
        tariff_code,
        recipient,
        packages,
        *,
        contract_type,
        number=None,
        comment=None,
        developer_key=None,
        shipment_point=None,
        delivery_point=None,
        date_invoice=None,
        shipper_name=None,
        shipper_address=None,
        delivery_recipient_cost=None,
        delivery_recipient_cost_adv=None,
        sender=None,
        seller=None,
        from_location=None,
        to_location=None,
        services=None,
        request_print=None,
        origin_response=False,
        **kwargs,
    ):
        """
        Register an order

        Параметры повторяют поля тела запроса, поэтому состав вложенных структур —
        `recipient`, `packages`, адресов и прочих — здесь не дублируется. Он описан
        по полям в
        [документации CDEK](https://apidoc.cdek.ru/#tag/order/operation/register_1)
        и остаётся источником истины: там же видно, какие поля обязательны для
        конкретного типа заказа.

        В тело запроса попадают только переданные параметры: непереданные остаются
        равными `None` и отбрасываются. Всё остальное уходит как есть — пустая строка
        для СДЭК осмысленное значение, а не отсутствие поля.

        Даты передаются строками в формате `yyyy-MM-dd`: тело сериализуется штатным
        JSON-энкодером `requests`, и объект `datetime.date` вызовет `TypeError`.

        Args:
            tariff_code (int): Код тарифа, см.
                [приложение 4](https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK).
            recipient (dict): Получатель.
            packages (list of dict): Места (упаковки) заказа вместе с товарами.
            contract_type (ContractType): Тип заказа. Уходит в поле `type`.
            number (str, optional): Номер заказа в ИС клиента. Только для заказов
                «интернет-магазин». Если не передан, СДЭК присвоит собственный uuid.
            comment (str, optional): Комментарий к заказу.
            developer_key (str, optional): Ключ разработчика, для разработчиков модулей.
            shipment_point (str, optional): Код ПВЗ СДЭК, откуда забирают отправление
                либо куда клиент привозит его сам.
            delivery_point (str, optional): Код ПВЗ СДЭК, куда доставить посылку.
            date_invoice (str, optional): Дата инвойса в формате `yyyy-MM-dd`.
            shipper_name (str, optional): Грузоотправитель.
            shipper_address (str, optional): Адрес грузоотправителя.
            delivery_recipient_cost (dict, optional): Доп. сбор за доставку, который
                интернет-магазин берёт с получателя. Валюта сбора должна совпадать
                с валютой наложенного платежа.
            delivery_recipient_cost_adv (list of dict, optional): Доп. сбор за доставку
                в зависимости от суммы заказа.
            sender (dict, optional): Отправитель.
            seller (dict, optional): Реквизиты истинного продавца. Код формы
                собственности см. в
                [приложении 5](https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-5.-Forma-sobstvennosti).
            from_location (dict, optional): Адрес отправления. Не нужен, если задан
                `shipment_point`.
            to_location (dict, optional): Адрес получения. Не нужен, если задан
                `delivery_point`.
            services (list of dict, optional): Дополнительные услуги, см.
                [приложение 6](https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-6.-Dopolnitelnye-uslugi).
            request_print (str, optional): Печатная форма, которую нужно сформировать по
                заказу: `barcode` — ШК мест, `waybill` — квитанция. Уходит в поле `print`.
            origin_response (bool, optional): Вернуть ответ целиком вместо созданного
                заказа. Defaults to False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            dict | Response: Созданный заказ, а при `origin_response=True` — ответ целиком.

        Raises:
            CdekRequestException: Ответ с ошибочным статусом.
        """

        payload = drop_none(
            {
                "type": ContractType(contract_type).value,
                "tariff_code": tariff_code,
                "recipient": recipient,
                "packages": packages,
                "number": number,
                "comment": comment,
                "developer_key": developer_key,
                "shipment_point": shipment_point,
                "delivery_point": delivery_point,
                "date_invoice": date_invoice,
                "shipper_name": shipper_name,
                "shipper_address": shipper_address,
                "delivery_recipient_cost": delivery_recipient_cost,
                "delivery_recipient_cost_adv": delivery_recipient_cost_adv,
                "sender": sender,
                "seller": seller,
                "from_location": from_location,
                "to_location": to_location,
                "services": services,
                "print": request_print,
            }
        )

        response = self.send(self.RESOURCE_ORDER, method="post", data=payload, **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def get_order(
        self, uuid=None, cdek_number=None, im_number=None, raise_errors=True, origin_response=False, **kwargs
    ):
        """
        Get order info

        By CDEK/IM number: https://apidoc.cdek.ru/#tag/order/operation/get
        By UUID: https://apidoc.cdek.ru/#tag/order/operation/get_2

        Args:
            uuid (str): CDEK order uuid
            cdek_number (str): CDEK order id (aka tracknumber)
            im_number (str): Store order id
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: order info
        """

        if sum([bool(uuid), bool(cdek_number), bool(im_number)]) != 1:
            raise Exception("Only one of the `uuid` or `cdek_number` or `im_number` options must be specified")

        url = Path(self.RESOURCE_ORDER)
        if uuid:
            url /= Path(uuid)

        elif cdek_number:
            kwargs["params"] = {"cdek_number": cdek_number}

        elif im_number:
            kwargs["params"] = {"im_number": im_number}

        response = self.send(url, method="get", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def remove_order(self, uuid, raise_errors=True):
        """
        Remove order

        https://apidoc.cdek.ru/#tag/order/operation/delete

        Args:
            uuid (str): order cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)

        Returns:
            dict: deleted order info
        """

        return self.send(Path(self.RESOURCE_ORDER) / Path(uuid), method="delete", raise_errors=raise_errors)

    def registrate_intakes(
        self,
        intake_date,
        intake_time_from,
        intake_time_to,
        order_uuid=None,
        lunch_time_from=None,
        lunch_time_to=None,
        name=None,
        cdek_number=None,
        weight=None,
        length=None,
        width=None,
        height=None,
        comment=None,
        sender=None,
        from_location=None,
        need_call=None,
        raise_errors=True,
        origin_response=False,
    ):
        """
        Registrate intakes

        https://apidoc.cdek.ru/#tag/intake/operation/create

        Args:
            intake_date (str): Дата ожидания курьера в формате (yyyy-MM-dd)
            intake_time_from (time): Время начала ожидания курьера
            intake_time_to (time): Время окончания ожидания курьера
            order_uuid (str, optional): Идентификатор заказа в ИС СДЭК (UUID)
            lunch_time_from (time, optional): Время начала обеда, должно входить в диапазон
                [intake_time_to;intake_time_to]
            lunch_time_to (time, optional): Время окончания обеда, должно входить в диапазон
                [intake_time_to;intake_time_to]
            name (str, optional): Описание груза
            cdek_number (int, optional): Номер заказа СДЭК
            weight (int, optional): Общий вес (в граммах)
            length (int, optional): Габариты упаковки. Длина (в сантиметрах)
            width (int, optional): Габариты упаковки. Ширина (в сантиметрах)
            height (int, optional): Габариты упаковки. Высота (в сантиметрах)
            comment (str, optional): Комментарий к заявке для курьера
            sender (dict, optional): Отправитель:
                name (str): ФИО контактного лица
                company (str, optional): Название компании отправителя
                phones (list of dict, optional): Список телефонов:
                    number (str): Номер телефона
                    additional (str, optional): Дополнительная информация (доп. номер)
            from_location (dict, optional): Адрес отправителя (забора):
                country_code (str): Код страны в формате ISO_3166-1_alpha-2
                address (str): Строка адреса
                code (str, optional): Код локации (справочник СДЭК)
                fias_guid (str, optional): Уникальный идентификатор ФИАС (UUID)
                postal_code (str, optional): Почтовый индекс
                longitude (float, optional): Долгота
                latitude (float, optional): Широта
                region (str, optional): Название региона
                sub_region (str, optional): Название района региона
                city (str, optional): Название города
                kladr_code (str, optional): Код КЛАДР
            need_call (bool, optional): Необходим прозвон отправителя (по умолчанию - false)
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: Intakes dict
        """

        complete_data = clear_dict(
            {
                "intake_date": intake_date,
                "intake_time_from": intake_time_from,
                "intake_time_to": intake_time_to,
                "order_uuid": order_uuid,
                "lunch_time_from": lunch_time_from,
                "lunch_time_to": lunch_time_to,
                "name": name,
                "cdek_number": cdek_number,
                "weight": weight,
                "length": length,
                "width": width,
                "height": height,
                "comment": comment,
                "sender": sender,
                "from_location": from_location,
                "need_call": need_call,
            }
        )

        response = self.send(self.RESOURCE_INTAKES, method="post", data=complete_data, raise_errors=raise_errors)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def get_intakes(self, uuid, raise_errors=True, origin_response=False):
        """
        Get intakes info

        https://apidoc.cdek.ru/#tag/intake/operation/getByUuid

        Args:
            uuid (str): intakes cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: intakes info
        """

        response = self.send(Path(self.RESOURCE_INTAKES) / Path(uuid), method="get", raise_errors=raise_errors)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def remove_intakes(self, uuid, raise_errors=True):
        """
        Remove intakes

        https://apidoc.cdek.ru/#tag/intake/operation/deleteByUuid

        Args:
            uuid (str): intakes cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)

        Returns:
            dict: deleted intakes info
        """

        return self.send(Path(self.RESOURCE_INTAKES) / Path(uuid), method="delete", raise_errors=raise_errors)

    def get_regions(
        self,
        country_codes: list[str] | None = None,
        region_code: str | None = None,
        kladr_region_code: str | None = None,
        fias_region_guid: str | None = None,
        size: int | None = 1000,
        page: int | None = 0,
        lang: str | None = None,
        raise_errors: bool | None = True,
        origin_response: bool | None = False,
    ) -> list:
        """
        Request regions

        https://apidoc.cdek.ru/#tag/location/operation/regions

        Args:
            country_codes           Массив кодов стран в формате  ISO_3166-1_alpha-2    string(2) [ ]   нет
            region_code             Код региона СДЭК    string(255) нет
            kladr_region_code       Код КЛАДР региона   string(255) нет
            fias_region_guid        Уникальный идентификатор ФИАС региона   UUID    нет
            size                    Ограничение выборки результата. По умолчанию 1000   integer да, если указан page
            page                    Номер страницы выборки результата. По умолчанию 0   integer нет
            lang                    Локализация. По умолчанию "rus" string(3)   нет
            raise_errors            raise errors? (default: True)
            origin_response         return original response or only entity? (default: False)

        Returns:
            list: list of regions
        """

        complete_data = clear_dict(
            {
                "country_codes": country_codes,
                "region_code": region_code,
                "kladr_region_code": kladr_region_code,
                "fias_region_guid": fias_region_guid,
                "size": size,
                "page": page,
                "lang": lang,
            }
        )

        response = self.send(Path(self.RESOURCE_REGIONS), method="get", params=complete_data, raise_errors=raise_errors)

        if not origin_response:
            response = response.json()

        return response

    def get_all_regions(self, **kwargs):
        request_kwargs = deepcopy(kwargs)
        request_kwargs["page"] = 0
        request_kwargs["origin_response"] = False

        while True:
            regions = self.get_regions(**request_kwargs)

            if len(regions) == 0:
                break

            yield from regions

            request_kwargs["page"] += 1

    def get_cities(
        self,
        country_codes=None,
        region_code=None,
        kladr_region_code=None,
        fias_region_guid=None,
        kladr_code=None,
        fias_guid=None,
        postal_code=None,
        code=None,
        city=None,
        page=0,
        size=1000,
        lang=None,
        payment_limit=None,
        raise_errors=True,
        origin_response=False,
    ):
        """
        Request regions

        https://apidoc.cdek.ru/#tag/location/operation/cities

        Args:
            country_codes           Массив кодов стран в формате  ISO_3166-1_alpha-2    string(2) [ ]   нет
            region_code             Код региона СДЭК    string(255) нет
            kladr_region_code       Код КЛАДР региона   string(255) нет
            fias_region_guid        Уникальный идентификатор ФИАС региона UUID    нет
            kladr_code              Код КЛАДР населенного пункта    string(255) нет
            fias_guid               Уникальный идентификатор ФИАС населенного пункта    UUID    нет
            postal_code             Почтовый индекс string(255) нет
            code                    Код населенного пункта СДЭК string(255) нет
            city                    Название населенного пункта. Должно соответствовать полностью   string(255) нет
            size                    Ограничение выборки результата. По умолчанию 1000   integer да, если указан page
            page                    Номер страницы выборки результата. По умолчанию 0   integer нет
            lang                    Локализация. По умолчанию "rus" string(3)   нет
            payment_limit           Ограничение на сумму наложенного платежа:
                -1 - ограничения нет;
                 0 - наложенный платеж не принимается;
                 положительное значение - сумма наложенного платежа не более данного значения.
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            list: list of cities
        """

        complete_data = clear_dict(
            {
                "country_codes": country_codes,
                "region_code": region_code,
                "kladr_region_code": kladr_region_code,
                "fias_region_guid": fias_region_guid,
                "kladr_code": kladr_code,
                "fias_guid": fias_guid,
                "postal_code": postal_code,
                "code": code,
                "city": city,
                "page": page,
                "size": size,
                "lang": lang,
                "payment_limit": payment_limit,
            }
        )

        response = self.send(Path(self.RESOURCE_CITIES), method="get", params=complete_data, raise_errors=raise_errors)

        if not origin_response:
            response = response.json()

        return response

    def get_all_cities(self, **kwargs):
        request_kwargs = deepcopy(kwargs)
        request_kwargs["page"] = 0
        request_kwargs["origin_response"] = False

        while True:
            cities = self.get_cities(**request_kwargs)

            if len(cities) == 0:
                break

            yield from cities

            request_kwargs["page"] += 1

    def request_receipt(
        self,
        orders: list[dict],
        copy_count: int | None = None,
        form_type: str | None = None,
        origin_response: bool = False,
        **kwargs,
    ):
        """
        Request for the receipt of an order.

        Args:
            orders (list of dict): Список заказов:
                order_uuid (str, optional): Идентификатор заказа в ИС СДЭК
                cdek_number (str, optional): Номер заказа СДЭК
            copy_count (integer, optional): Число копий одной квитанции на листе. Рекомендовано указывать
                не менее 2, одна приклеивается на груз, вторая остается у отправителя (default: 2)
            form_type (bool, optional): Форма квитанции. Может принимать значения:
                tpl_china - квитанция на китайском
                tpl_armenia - квитанция на армянском
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: requested invoice dict

        https://apidoc.cdek.ru/#tag/print/operation/waybillPrint
        """

        complete_data = clear_dict(
            {
                "orders": orders,
                "copy_count": copy_count,
                "type": form_type,
            }
        )

        kwargs["data"] = complete_data
        response = self.send(self.RESOURCE_RECEIPT, method="post", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def request_barcode(
        self,
        orders: list[dict],
        copy_count: int | None = None,
        format_type: str | None = None,
        lang: str | None = None,
        origin_response: bool = False,
        **kwargs,
    ):
        """
        Request for the BARCODE of an order

        Args:
            orders (list of dict): Список заказов:
                order_uuid (str, optional): Идентификатор заказа в ИС СДЭК
                cdek_number (str, optional): Номер заказа СДЭК
            copy_count (integer, optional): Число копий одной квитанции на листе. Рекомендовано указывать
                не менее 2, одна приклеивается на груз, вторая остается у отправителя (default: 2)
            form_type (str, optional): Формат печати. Может принимать значения: A4, A5, A6
                (A - буква латинского алфавита). По умолчанию A4.
            lang (str, optional): Язык печатной формы. Возможные языки в кодировке ISO - 639-3:
                * Русский - RUS
                * Английский - ENG
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: requested invoice dict

        https://apidoc.cdek.ru/#tag/print/operation/barcodePrint
        """

        complete_data = clear_dict(
            {
                "orders": orders,
                "copy_count": copy_count,
                "format": format_type,
                "lang": lang,
            }
        )

        kwargs["data"] = complete_data
        response = self.send(self.RESOURCE_BARCODE, method="post", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def get_receipt(self, uuid, origin_response=False, **kwargs):
        """
        Receiving a receipt for the order.

        Args:
            uuid (str): intakes cdek uuid
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: requested invoice dict

        https://apidoc.cdek.ru/#tag/print/operation/waybillGet
        """

        response = self.send(Path(self.RESOURCE_RECEIPT) / Path(uuid), method="get", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def get_barcode(self, uuid, origin_response=False, **kwargs):
        """
        Receiving a get_barcode for the order.

        Args:
            uuid (str): intakes cdek uuid
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: requested barcode dict

        https://apidoc.cdek.ru/#tag/print/operation/barcodeGet
        """

        response = self.send(Path(self.RESOURCE_BARCODE) / Path(uuid), method="get", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def download(self, url, origin_response=False, **kwargs):
        """
        Download document.

        Args:
            url (str): cdek url
            origin_response (bool, optional): return original response or only entity? (default: False)
        """
        response = self.send(url, method="get", **kwargs)

        if origin_response:
            return response

        file = BytesIO()
        file.write(response.content)
        return file

    def get_shipping_cost(
        self,
        goods,
        version="1.0",
        auth_login=None,
        secure=None,
        date_execute=None,
        lang=None,
        sender_country_code=None,
        receiver_country_code=None,
        sender_city_id=None,
        sender_city=None,
        sender_city_post_code=None,
        receiver_city_id=None,
        receiver_city_post_code=None,
        receiver_city=None,
        sender_longitude=None,
        receiver_longitude=None,
        sender_latitude=None,
        receiver_latitude=None,
        tariff_id=None,
        tariff_list=None,
        services=None,
        auth=False,
        raise_errors=True,
        origin_response=False,
        **kwargs,
    ):
        """

        TODO:
        * new method https://apidoc.cdek.ru/#tag/calculator/operation/tariff

        goods (dict): Габаритные характеристики упаковки:
            weight (float): Вес упаковки (в килограммах)
            length (int): Длина упаковки (в сантиметрах)
            width (int):  Ширина упаковки (в сантиметрах)
            height (int): Высота упаковки (в сантиметрах)
            volume (float): Объём упаковки (в м³)
        version (str, optional): Версия используемого API - “1.0”
        auth_login (str, optional):  Идентификатор ИМ (логин)
        secure (str, optional): Ключ
        date_execute (date, optional): Планируемая дата отправки заказа в формате “ГГГГ-ММ-ДД” date    нет
        lang (str, optional): Локализация названий городов. По умолчанию "rus"
        sender_country_code (str, optional): Код страны отправителя в формате ISO_3166-1_alpha-2
            (см. “Общероссийский классификатор стран мира”). По умолчанию - ru.
        receiver_country_code (str, optional): Код страны получателя в формате ISO_3166-1_alpha-2
            (см. “Общероссийский классификатор стран мира”). По умолчанию - ru.
        sender_city_id (int, optional): Код города отправителя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
        sender_city (str, optional): Наименование города отправителя string  нет
        sender_city_post_code (int, optional): Индекс города отправителя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
        receiver_city_id (int, optional): Код города получателя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
        receiver_city_post_code (int, optional): Индекс города получателя из базы СДЭК
            (см. файл «City_XXX_YYYYMMDD.xls»)
        receiver_city (, optional): Наименование города получателя  string  нет
        sender_longitude (float, optional): Долгота города отправителя
        receiver_longitude (float, optional): Долгота города получателя
        sender_latitude (float, optional): Широта города отправителя
        receiver_latitude (float, optional): Широта города получателя
        tariff_id (int, optional): Код выбранного тарифа (подробнее см. приложение 1)
        tariff_list (list, optional): Список тарифов:
            priority (int): Заданный приоритет
            id (int): Код тарифа (подробнее см. приложение 1)
            mode_id (int, optional): Режим доставки (подробнее см. приложение 1)
        services (dict, optional): Список передаваемых дополнительных услуг (подробнее см. приложение 2):
            id (int): Идентификатор номера дополнительной услуги
            param (int, optional): Параметр дополнительной услуги, если необходимо
        raise_errors (bool, optional): raise errors? (default: True)
        origin_response (bool, optional): return original response or only entity? (default: False)

        https://apidoc.cdek.ru/#tag/calculator/operation/tariff
        """

        complete_data = clear_dict(
            {
                "goods": goods,
                "version": version,
                "dateExecute": date_execute,
                "lang": lang,
                "senderCountryCode": sender_country_code,
                "receiverCountryCode": receiver_country_code,
                "senderCityId": sender_city_id,
                "senderCity": sender_city,
                "senderCityPostCode": sender_city_post_code,
                "receiverCityId": receiver_city_id,
                "receiverCityPostCode": receiver_city_post_code,
                "receiverCity": receiver_city,
                "senderLongitude": sender_longitude,
                "receiverLongitude": receiver_longitude,
                "senderLatitude": sender_latitude,
                "receiverLatitude": receiver_latitude,
                "tariffId": tariff_id,
                "tariffList": tariff_list,
                "services": services,
            }
        )

        if auth:
            if not self.client_id or not self._client_secret:
                raise CdekNoAuthClientException("Has no provide auth information")

            if "dateExecute" not in complete_data:
                complete_data["dateExecute"] = dt.date.today().isoformat()

            complete_data["authLogin"] = self.client_id
            complete_data["secure"] = get_secure(self._client_secret, complete_data["dateExecute"])

        kwargs["raise_errors"] = raise_errors
        kwargs["data"] = complete_data

        response = self.send(self.RESOURCE_CALCULATOR_URL, method="post", **kwargs)

        if not origin_response:
            response = response.json()

        return response

    def calculator_tariff(
        self,
        tariff_code,
        from_location,
        to_location,
        packages,
        *,
        contract_type,
        date=None,
        currency=None,
        services=None,
        origin_response=False,
        **kwargs,
    ):
        """
        tariff_code (int): Код тарифа
        from_location (dict): Адрес отправления
            code (int, optional): Код населенного пункта СДЭК (метод "Список населенных пунктов")
            postal_code (str, optional): Почтовый индекс
            country_code (str, optional): Код страны в формате ISO_3166-1_alpha-2
            city (str, optional): Название города
            address (str, optional): Полная строка адреса
        to_location (dict): Адрес получения
            code (int, optional): Код населенного пункта СДЭК (метод "Список населенных пунктов")
            postal_code (str, optional): Почтовый индекс
            country_code (str, optional): Код страны в формате ISO_3166-1_alpha-2
            city (str, optional): Название города
            address (str, optional): Полная строка адреса
        packages (list of dict): Список информации по местам (упаковкам)
            weight (int): Общий вес (в граммах)
            length (int, optional): Габариты упаковки. Длина (в сантиметрах)
            width (int, optional):  Габариты упаковки. Ширина (в сантиметрах)
            height (int, optional): Габариты упаковки. Высота (в сантиметрах)
        contract_type (ContractType): Тип заказа, от него зависят доступные тарифы.
            Уходит в поле `type`.
        date (str, optional): Дата и время планируемой передачи заказа. По умолчанию - текущая.
        currency (int, optional): Валюта, в которой необходимо произвести расчет. По умолчанию - валюта договора
        services (list of dict, optional): Дополнительные услуги
            code (string): Тип дополнительной услуги, код из справочника доп. услуг
            parameter (string, optional): Параметр дополнительной услуги
        origin_response (bool, optional): return original response or only entity? (default: False)

        https://apidoc.cdek.ru/#tag/calculator/operation/tariff
        """

        kwargs["data"] = clear_dict(
            {
                "type": ContractType(contract_type).value,
                "tariff_code": tariff_code,
                "from_location": from_location,
                "to_location": to_location,
                "packages": packages,
                "date": date,
                "currency": currency,
                "services": services,
            }
        )
        response = self.send(self.RESOURCE_CALCULATOR_TARIFF, method="post", **kwargs)

        if not origin_response:
            response = response.json()

        return response

    def subscribe(self, url, type, raise_errors=True, origin_response=False):
        """
        Webhook subscribe

        https://apidoc.cdek.ru/#tag/webhook/operation/createWebhook
        """

        complete_data = clear_dict(
            {
                "url": url,
                "type": type,
            }
        )

        response = self.send(self.RESOURCE_SUBSCRIPTION, method="post", data=complete_data, raise_errors=raise_errors)

        if not origin_response:
            response = response.json()

        return response

    def subscribe_info(self, raise_errors=True, origin_response=False):
        """
        information about all current subscriptions

        https://apidoc.cdek.ru/#tag/webhook/operation/getAll
        """

        response = self.send(Path(self.RESOURCE_SUBSCRIPTION), method="get", raise_errors=raise_errors)

        if not origin_response:
            response = response.json()

        return response

    def subscribe_info_by_uuid(self, uuid, raise_errors=True, origin_response=False):
        """
        subscription information, where uuid is the subscription identifier

        https://apidoc.cdek.ru/#tag/webhook/operation/getById
        """

        response = self.send(Path(self.RESOURCE_SUBSCRIPTION) / Path(uuid), method="get", raise_errors=raise_errors)

        if not origin_response:
            response = response.json()

        return response

    def subscribe_delete(self, uuid, raise_errors=True, origin_response=False):
        """
        request to delete a subscription

        https://apidoc.cdek.ru/#tag/webhook/operation/deleteById
        """

        response = self.send(Path(self.RESOURCE_SUBSCRIPTION) / Path(uuid), method="delete", raise_errors=raise_errors)

        if not origin_response:
            response = response.json()

        return response

    def get_deliverypoints(
        self,
        postal_code1: int | None = None,
        city_code1: int | None = None,
        tipe: str | None = None,
        country_code: str | None = None,
        region_code: int | None = None,
        have_cashless: bool | None = None,
        have_cash: bool | None = None,
        allowed_cod: bool | None = None,
        is_dressing_room: bool | None = None,
        weight_max: int | None = None,
        weight_min: int | None = None,
        lang: str | None = None,
        take_only: bool | None = None,
        is_handout: bool | None = None,
        raise_errors: bool = True,
        origin_response: bool = False,
    ) -> list[dict] | Response:
        """
        Request delivery points

        https://apidoc.cdek.ru/#tag/delivery_point/operation/search

        Args:
            postal_code1                Почтовый индекс города, для которого необходим список офисов
                                        integer         нет
            city_code1                  Код города по базе СДЭК             integer         нет
            tipe                        Тип офиса, может принимать значения:
                «PVZ» - для отображения только складов СДЭК;
                «POSTAMAT» - для отображения постаматов СДЭК;
                «ALL» - для отображения всех ПВЗ независимо от их типа.
                При отсутствии параметра принимается значение по умолчанию «ALL».       string(8)       нет
            country_code                Код страны в формате ISO_3166-1_alpha-2
                                        (см. “Общероссийский классификатор стран мира”)
                                        string (2)  нет
            region_code                 Код региона по базе СДЭК    integer
            have_cashless               Наличие терминала оплаты     boolean     нет
            have_cash                   Есть прием наличных     boolean     нет
            allowed_cod                 Разрешен наложенный платеж     boolean     нет
            is_dressing_room            Наличие примерочной     boolean     нет
            weight_max                  Максимальный вес в кг, который может принять офис (значения больше 0 -
                                        передаются офисы, которые принимают этот вес; 0 - офисы с нулевым
                                        весом не передаются; значение не указано - все офисы). integer нет
            weight_min                  Минимальный вес в кг, который принимает офис (при переданном значении
                                        будут выводиться офисы с минимальным весом до указанного значения)
                                        integer нет
            lang                        Локализация офиса. По умолчанию "rus".  string(3)   нет
            take_only                   Является ли офис только пунктом выдачи     boolean     нет
            is_handout                  Является пунктом выдачи     boolean     нет

            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            list: list of delivery points
        """

        complete_data = clear_dict(
            {
                "postal_code1": postal_code1,
                "city_code1": city_code1,
                "type": tipe,
                "country_code": country_code,
                "region_code": region_code,
                "have_cashless": have_cashless,
                "have_cash": have_cash,
                "allowed_cod": allowed_cod,
                "is_dressing_room": is_dressing_room,
                "weight_max": weight_max,
                "weight_min": weight_min,
                "lang": lang,
                "take_only": take_only,
                "is_handout": is_handout,
            }
        )

        response = self.send(
            Path(self.RESOURCE_DELIVERYPOINTS), method="get", params=complete_data, raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()

        return response
