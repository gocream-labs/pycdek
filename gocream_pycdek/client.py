import datetime as dt
import logging
import warnings
from collections.abc import Iterator
from enum import IntEnum
from io import BytesIO
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

    Указывается в каждом заказе, а не в клиенте: тип - свойство заказа, а не учётной записи. `DELIVERY` доступен любому
    договору, `ONLINE_STORE` - только договору с интернет-магазином, поэтому одна и та же учётная запись может
    отправлять оба типа.

    Attributes:
        ONLINE_STORE: Заказ "интернет-магазин".
        DELIVERY: Заказ "доставка".
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

    Клиент держит открытую HTTP-сессию, поэтому у него есть время жизни. Соединение переиспользуется между запросами,
    и это тем выгоднее, чем дольше живёт экземпляр - один клиент на приложение предпочтительнее клиента на запрос.

    Освобождать соединения нужно явно, через `close` или блок `with`:

    ```python
    with CdekClient("id", "secret") as client:
        regions = client.get_regions()
    ```

    Без этого сокеты остаются открытыми, пока на клиента есть хоть одна ссылка. Сборщик мусора их в итоге доберёт,
    но предупреждения при этом не будет, так что накопление дескрипторов легко не заметить.
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
    """
    Насколько раньше срока клиент идёт за новым токеном. Запас нужен на расхождение часов с СДЭК и на время запроса,
    который этим токеном уйдёт. СДЭК выдаёт токен на час, так что пять минут стоят примерно 8% срока жизни.
    """

    DEFAULT_TIMEOUT: tuple[float, float] = (3, 7)
    """
    Таймаут запроса как пара `(connect, read)` в секундах. Отдельный атрибут, а не литерал в `send`, чтобы значение
    переопределялось наследником или на экземпляре, без правки вызовов.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = PRODUCTION_API_URL,
    ) -> None:
        """
        Args:
            client_id: Идентификатор клиента СДЭК, передаваемый в query-поле `client_id` при авторизации.
            client_secret: Секретный ключ клиента СДЭК, передаваемый в query-поле `client_secret` при авторизации.
            base_url: Базовый URL API. По умолчанию рабочий `https://api.cdek.ru`. Для тестового контура используйте
                `https://api.edu.cdek.ru`.
        """

        self.client_id = client_id
        self._client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None
        self._token_expires_at: dt.datetime | None = None

        # Сессия держит TCP-соединение открытым между запросами. На пагинации
        # `get_all_cities` это разница между одним handshake и сотнями.
        self._session = requests.Session()

    def __enter__(self) -> "CdekClient":
        """
        Enter runtime context and return the client itself
        """

        return self

    def __exit__(self, *exc_info: object) -> None:
        """
        Leave runtime context, closing the client and releasing its connections
        """

        self.close()

    def close(self) -> None:
        """
        Close underlying HTTP session and release pooled connections

        Вызывается автоматически при выходе из блока `with`. Клиент после закрытия остаётся работоспособным: следующий
        запрос откроет соединение заново.
        """

        self._session.close()

    @property
    def token(self) -> str:
        """
        Return a cached token, refreshing it before expiration

        Срок действия берётся из JWT. Обновление выполняется заранее с учётом `TOKEN_REFRESH_MARGIN` через
        [`authorization`][gocream_pycdek.client.CdekClient.authorization].
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

    def authorization(self) -> dict:
        """
        Request an access token

        Учётные данные отправляются в query-параметрах POST-запроса. Метод только запрашивает токен и возвращает ответ
        API как есть, без кэширования. Кэш токена обновляется отдельно, свойством
        [`token`][gocream_pycdek.client.CdekClient.token].

        [документации CDEK](https://apidoc.cdek.ru/#tag/auth/operation/getOAuthToken)

        Returns:
            JSON-ответ с токеном и сведениями о сроке действия.

        Raises:
            CdekApiAccessException: API вернул `invalid_client`.
            CdekApiUnavailableException: HTTP 503 или сообщение "Service Unavailable" без кода ошибки.
            CdekApiException: Другая ошибка авторизации.
            CdekApiWrongTokenTypeException: Получен неподдерживаемый тип токена.
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

            try:
                error = response.json()
            except ValueError:
                pass
            else:
                if isinstance(error, dict):
                    code = error.get("error")
                    message = error.get("error_description") or error.get("reason") or message

            if code == "invalid_client":
                raise CdekApiAccessException(message)

            if response.status_code == 503 or (code is None and message == "Service Unavailable"):
                raise CdekApiUnavailableException()

            raise CdekApiException(message, code)

        payload = response.json()
        if payload["token_type"] != "bearer":
            raise CdekApiWrongTokenTypeException(payload["token_type"])

        return payload

    def get_url(self, resource: str | PurePath) -> str:
        """
        Build a request URL

        Относительный путь дополняется базовым URL. Абсолютный URL нужно передавать строкой: `PurePath` теряет двойной
        слэш в схеме при создании объекта.

        Args:
            resource (str|PurePath): Путь ресурса относительно `base_url` или абсолютный URL. Ведущий `/` отбрасывается.

        Returns:
            str: Полный URL запроса. Абсолютный URL возвращается без изменений.
        """

        resource = resource.as_posix() if isinstance(resource, PurePath) else str(resource)
        if resource.startswith(("http://", "https://")):
            return resource

        return f"{self.base_url}/{resource.lstrip('/')}"

    def get_headers(self) -> dict[str, str]:
        """
        Build authorization headers

        Использует [`token`][gocream_pycdek.client.CdekClient.token], при необходимости обновляя его.
        """

        return {"Authorization": f"Bearer {self.token}"}

    def send(
        self,
        resource: str | PurePath,
        method: str,
        *,
        data: dict | None = None,
        params: dict | None = None,
        raise_errors: bool = True,
        **kwargs,
    ) -> Response:
        """
        Send authorized request to the API

        Args:
            resource (str|PurePath): Resource path or an absolute url.
            method (str): HTTP method, e.g. `get`, `post` or `delete`.
            data (dict, optional): Request body, sent as json. Defaults to None.
            params (dict, optional): Query string parameters. Defaults to None.
            raise_errors (bool, optional): Raise `CdekRequestException` on error status. Defaults to True.
            **kwargs: Passed to `requests.Session.request` as is. Свой `headers` заменяет набор целиком, а не дополняет
                его: так подменяется `Authorization` или отправляется анонимный запрос, если передать `headers={}`.

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

        Параметры повторяют поля тела запроса, поэтому состав вложенных структур - `recipient`, `packages`, адресов
        и прочих - здесь не дублируется. Он описан по полям в
        [документации CDEK](https://apidoc.cdek.ru/#tag/order/operation/register_1) и остаётся источником истины:
        там же видно, какие поля обязательны для конкретного типа заказа.

        В тело запроса попадают только переданные параметры: непереданные остаются равными `None` и отбрасываются. Всё
        остальное уходит как есть - пустая строка для СДЭК осмысленное значение, а не отсутствие поля.

        Даты передаются строками в формате `yyyy-MM-dd`: тело сериализуется штатным JSON-энкодером `requests`, и объект
        `datetime.date` вызовет `TypeError`.

        Args:
            tariff_code (int): Код тарифа СДЭК. Обязателен для регистрации заказа.
            recipient (dict): Получатель. Обязательны `name` (ФИО, до 255 символов) и `phones` (не более 10 номеров).
                Остальные поля описаны в схеме получателя API.
            packages (list of dict): Список мест (упаковок) с товарами: от 1 до 255 мест. Состав упаковки и товаров
                описан в схеме `PackageRequestDto` документации регистрации заказа.
            contract_type (ContractType): Тип заказа: `1` (`ContractType.ONLINE_STORE`) - интернет-магазин, только для
                договора с ИМ; `2` (`ContractType.DELIVERY`) - доставка для любого договора. Клиент требует явного
                значения и передаёт его в поле `type`.
            number (str, optional): Номер заказа в ИС клиента для типа "интернет-магазин", до 40 ASCII-символов. Должен
                быть уникальным среди активных неудалённых заказов одного договора. Повтор разрешён, если предыдущий
                заказ завершён со статусом `DELIVERED` или `NOT_DELIVERED`.
            comment (str, optional): Комментарий к заказу, до 255 символов.
            developer_key (str, optional): Ключ разработчика. Клиент передаёт его в поле тела `developer_key`.
                Спецификация также описывает отдельный HTTP-заголовок `developer-key`.
            shipment_point (str, optional): Код ПВЗ самостоятельного привоза, до 255 символов. Обязателен для тарифа
                "от склада". Несовместим с `from_location`.
            delivery_point (str, optional): Код ПВЗ назначения, до 255 символов. Обязателен для тарифа "до склада" или
                "до постамата". Несовместим с `to_location`.
            date_invoice (str, optional): Дата инвойса строкой `yyyy-MM-dd`. Обязательна для международного заказа типа
                "интернет-магазин". По документации заполнение поля делает заказ международным.
            shipper_name (str, optional): Грузоотправитель, до 255 символов. Обязателен для международного заказа типа
                "интернет-магазин". По документации заполнение поля делает заказ международным.
            shipper_address (str, optional): Адрес грузоотправителя, до 255 символов. Обязателен для международного
                заказа типа "интернет-магазин". По документации заполнение поля делает заказ международным.
            delivery_recipient_cost (dict, optional): Дополнительный сбор за доставку с получателя, только для
                интернет-магазина. Обязательное поле `value` - сумма с НДС, не более 50 000 000 в валюте города
                получателя. При переданном `vat_rate` нужен `vat_sum`. Для Беларусь-Беларусь и РФ-Беларусь поле
                игнорируется.
            delivery_recipient_cost_adv (list of dict, optional): Пороги дополнительного сбора за доставку в зависимости
                от суммы заказа. Применяются только для интернет-магазина с услугой "ЧАСТИЧНАЯ ДОСТАВКА". Правила
                расчёта при полном отказе от товара приведены в документации поля.
            sender (dict, optional): Отправитель: обязателен для типа "доставка", необязателен для интернет-магазина.
                В структуре обязательно `name`. `phones` содержит до 10 номеров и требуется, если номер отправителя
                не был указан при регистрации.
            seller (dict, optional): Реквизиты истинного продавца. Для отображения в чеке нужны `name`, `inn` и `phone`.
                Иначе используются реквизиты контрагента договора. `phone` обязателен при заданном `inn`. Дополнительно
                доступны `ownership_form` и `address`.
            from_location (dict, optional): Адрес отправления для тарифа "от двери". Обязательна строка `address`
                (до 255 символов). Населённый пункт задаётся полями схемы адреса. Несовместим с `shipment_point`.
            to_location (dict, optional): Адрес получения для тарифа "до двери". Обязательна строка `address`
                (до 255 символов). Населённый пункт задаётся полями схемы адреса. Несовместим с `delivery_point`.
            services (list of dict, optional): Список дополнительных услуг с кодом `code` и параметром `parameter`, если
                он требуется выбранной услугой. Значения перечислены в приложении 6 документации СДЭК.
            request_print (str, optional): Печатная форма, создаваемая вместе с заказом. Передаётся в поле `print`.
                Текущая спецификация перечисляет `WAYBILL` (квитанция) и `BARCODE` (штрихкоды). Клиент отправляет
                значение без изменения регистра.
            origin_response (bool, optional): Вернуть ответ целиком вместо созданного заказа. Defaults to False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            dict | Response: Созданный заказ, а при `origin_response=True` - ответ целиком.

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

    def get_order(self, uuid=None, cdek_number=None, im_number=None, *, origin_response=False, **kwargs):
        """
        Get an order by one of its identifiers

        Идентификатор выбирает метод API: по uuid заказ запрашивается
        [адресом ресурса](https://apidoc.cdek.ru/#tag/order/operation/get_2), по номеру СДЭК или по номеру в ИС клиента
        - [query-параметром](https://apidoc.cdek.ru/#tag/order/operation/get).

        Идентификатор нужен ровно один: без него искать нечего, а с двумя клиенту пришлось бы решать за пользователя,
        какой из них главный. Пустое значение считается непереданным - заказ по нему всё равно не найдётся, а запрос
        ушёл бы за списком.

        Ответ с ошибкой не содержит `entity`, поэтому `raise_errors=False` осмысленно только вместе с
        `origin_response=True`: иначе разбор такого ответа упадёт с `KeyError`.

        Args:
            uuid (str, optional): UUID заказа в ИС СДЭК для получения сведений по адресу `/v2/orders/{uuid}`.
            cdek_number (str, optional): Номер заказа СДЭК (трек-номер). Отправляется query-параметром `cdek_number`.
            im_number (str, optional): Номер заказа в ИС клиента. Отправляется query-параметром `im_number`. Клиент
                требует ровно один непустой идентификатор из `uuid`, `cdek_number`, `im_number`.
            origin_response (bool, optional): Вернуть ответ целиком вместо найденного заказа. Defaults to False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            dict | Response: Найденный заказ, а при `origin_response=True` - ответ целиком.

        Raises:
            ValueError: Идентификатор не передан либо передан не один.
            CdekRequestException: Ответ с ошибочным статусом.
        """

        identifiers = {"uuid": uuid, "cdek_number": cdek_number, "im_number": im_number}
        passed = [name for name, value in identifiers.items() if value]

        if len(passed) > 1:
            msg = "Only one of the `uuid` or `cdek_number` or `im_number` options must be specified"
            raise ValueError(msg)

        if len(passed) == 0:
            msg = "One of the `uuid` or `cdek_number` or `im_number` options must be specified"
            raise ValueError(msg)

        name = passed[0]
        if name == "uuid":
            resource, params = f"{self.RESOURCE_ORDER}/{uuid}", None
        else:
            resource, params = self.RESOURCE_ORDER, {name: identifiers[name]}

        response = self.send(resource, method="get", params=params, **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def remove_order(
        self, uuid: str, raise_errors: bool = True, origin_response: bool = False, **kwargs
    ) -> dict | Response:
        """
        Remove order

        https://apidoc.cdek.ru/#tag/order/operation/delete

        Args:
            uuid: Идентификатор заказа в ИС СДЭК, который необходимо удалить. Передаётся в пути запроса.
            raise_errors: Вызывать исключение при ошибочном статусе ответа. По умолчанию True.
            origin_response: Вернуть ответ целиком вместо `entity`. По умолчанию False. Используйте True вместе с
                `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ. Принятие запроса на удаление ещё
            не означает завершения удаления.

        Raises:
            CdekRequestException: Ответ с ошибочным статусом при `raise_errors=True`.
        """

        response = self.send(f"{self.RESOURCE_ORDER}/{uuid}", method="delete", raise_errors=raise_errors, **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

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
        **kwargs,
    ) -> dict | Response:
        """
        Registrate intakes

        https://apidoc.cdek.ru/#tag/intake/operation/create

        Args:
            intake_date (str): Дата ожидания курьера строкой `yyyy-MM-dd`, не более чем на 31 день вперёд от текущей.
                Заявка на сегодня, созданная после 15:00 по времени отправителя, может быть выполнена на следующий
                день.
            intake_time_from (str): Начало ожидания в формате `HH:mm`, не ранее 09:00 местного времени.
            intake_time_to (str): Окончание ожидания в формате `HH:mm`, не позднее 22:00 местного времени.
            order_uuid (str, optional): Идентификатор заказа в ИС СДЭК. По описанию API обязателен, если не передан
                `cdek_number`.
            lunch_time_from (str, optional): Начало обеда в формате `HH:mm`, внутри интервала от `intake_time_from` до
                `intake_time_to`.
            lunch_time_to (str, optional): Окончание обеда в формате `HH:mm`, внутри интервала ожидания курьера.
            name (str, optional): Описание груза, до 255 символов. Требуется без номера заказа, иначе берётся из
                заказа.
            cdek_number (int, optional): Номер заказа СДЭК. По описанию API обязателен, если не передан `order_uuid`.
            weight (int, optional): Общий вес в граммах. Если поле отсутствует, значение по умолчанию на стороне API -
                100.
            length (int, optional): Длина упаковки в сантиметрах. При отсутствии поля API использует 1.
            width (int, optional): Ширина упаковки в сантиметрах. При отсутствии поля API использует 1.
            height (int, optional): Высота упаковки в сантиметрах. При отсутствии поля API использует 1.
            comment (str, optional): Комментарий курьеру, до 255 символов.
            sender (dict, optional): Отправитель. Требуется без номера заказа, иначе берётся из заказа. Обязательно
                `name` (до 255 символов). `phones` содержит не более 10 номеров и требуется, если номер отправителя не
                указан в заказе. Дополнительные поля описаны в `IntakeContactDto`.
            from_location (dict, optional): Адрес забора. Требуется без номера заказа,
                иначе берётся из заказа. Обязательно `address` (до 255 символов). Доступны `code` (целочисленный код
                города СДЭК), `city_uuid`, `city`, `fias_guid`, `postal_code`, поля региона и координаты.
                `country_code` - ISO 3166-1 alpha-2, по умолчанию `RU`. Поля `kladr_code`, а также `fias_region_guid`
                и `kladr_region_code` в составе региона, помечены устаревшими в спецификации API.
            need_call (bool, optional): Нужен ли предварительный звонок отправителю. По умолчанию на стороне API -
                False.
            raise_errors (bool, optional): Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response (bool, optional): Вернуть исходный HTTP-ответ вместо `entity`. По умолчанию False.
                Используйте True вместе с `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            dict | Response: Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        complete_data = drop_none(
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

        response = self.send(
            self.RESOURCE_INTAKES, method="post", data=complete_data, raise_errors=raise_errors, **kwargs
        )

        if not origin_response:
            response = response.json()["entity"]

        return response

    def get_intakes(
        self, uuid: str, raise_errors: bool = True, origin_response: bool = False, **kwargs
    ) -> dict | Response:
        """
        Get intakes info

        https://apidoc.cdek.ru/#tag/intake/operation/getByUuid

        Args:
            uuid (str): Идентификатор заявки на вызов курьера в ИС СДЭК, о которой нужно получить сведения. Это UUID
                заявки, а не заказа.
            raise_errors (bool, optional): Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response (bool, optional): Вернуть исходный HTTP-ответ вместо `entity`. По умолчанию False.
                Используйте True вместе с `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            dict | Response: Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(f"{self.RESOURCE_INTAKES}/{uuid}", method="get", raise_errors=raise_errors, **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def remove_intakes(self, uuid: str, raise_errors: bool = True, **kwargs) -> Response:
        """
        Remove intakes

        https://apidoc.cdek.ru/#tag/intake/operation/deleteByUuid

        Args:
            uuid (str): Идентификатор заявки на вызов курьера в ИС СДЭК, которую необходимо удалить. Это UUID заявки,
                а не заказа.
            raise_errors (bool, optional): Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Response: Исходный HTTP-ответ. Принятие запроса ещё не означает завершения удаления.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        return self.send(f"{self.RESOURCE_INTAKES}/{uuid}", method="delete", raise_errors=raise_errors, **kwargs)

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
        **kwargs,
    ) -> list[dict] | dict | Response:
        """
        Request regions

        https://apidoc.cdek.ru/#tag/location/operation/regions

        Deprecated:
            `region_code`, `kladr_region_code`: Отсутствуют в текущей спецификации метода. Это не поле, помеченное
                устаревшим, а параметр, которого в контракте API никогда не было; поддержка на стороне API не
                подтверждена. Оставлены для обратной совместимости и будут удалены в 3.0.0.
            `fias_region_guid`: Помечено устаревшим в спецификации API - значения могут быть неактуальны.

        Args:
            country_codes: Список кодов стран ISO 3166-1 alpha-2. Клиент передаёт значение как query-параметр
                `country_codes`.
            region_code: Код региона СДЭК. См. секцию Deprecated выше.
            kladr_region_code: Код КЛАДР региона. См. секцию Deprecated выше.
            fias_region_guid: UUID региона ФИАС. См. секцию Deprecated выше.
            size: Размер страницы, по умолчанию 1000. По документации обязателен, если указан `page`. None исключает
                поле из запроса.
            page: Номер страницы, начиная с 0. По умолчанию 0. None исключает поле из запроса.
            lang: Локализация ответа: `rus` (по умолчанию API), `eng` или `zho`.
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Декодированный JSON (список при успешном ответе),
            при `raise_errors=False` возможен словарь с ошибкой,
            а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        if region_code is not None or kladr_region_code is not None:
            warnings.warn(
                "get_regions: `region_code` and `kladr_region_code` are absent from the current API v2 "
                "specification for this method; support is unconfirmed and both will be removed in 3.0.0",
                DeprecationWarning,
                stacklevel=2,
            )

        if fias_region_guid is not None:
            warnings.warn(
                "get_regions: `fias_region_guid` is deprecated by the CDEK API specification and may return "
                "stale values",
                DeprecationWarning,
                stacklevel=2,
            )

        complete_data = drop_none(
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

        response = self.send(
            self.RESOURCE_REGIONS, method="get", params=complete_data, raise_errors=raise_errors, **kwargs
        )

        if not origin_response:
            response = response.json()

        return response

    def get_all_regions(self, **kwargs) -> Iterator[dict]:
        """
        Iterate over all regions

        Обход начинается со страницы 0 и заканчивается на первом пустом списке. Переданные `page` и `origin_response`
        заменяются на 0 и False.

        Оставляйте `raise_errors=True`: обход ожидает список, а JSON-ошибка, возвращённая при отключённой проверке,
        не является страницей справочника.

        Args:
            **kwargs: Фильтры, размер страницы и HTTP-настройки для
                [`get_regions`][gocream_pycdek.client.CdekClient.get_regions].

        Yields:
            dict: Данные одного элемента справочника регионов.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        request_kwargs = kwargs.copy()
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
        **kwargs,
    ) -> list[dict] | dict | Response:
        """
        Request cities

        https://apidoc.cdek.ru/#tag/location/operation/cities

        Deprecated:
            `kladr_region_code`: Отсутствует в текущей спецификации метода. Это не поле, помеченное устаревшим,
                а параметр, которого в контракте API никогда не было; поддержка на стороне API не подтверждена. Оставлен
                для обратной совместимости и будет удалён в 3.0.0.
            `fias_region_guid`: Помечено устаревшим в спецификации API - значения могут быть неактуальны.

        Args:
            country_codes: Список кодов стран ISO 3166-1 alpha-2. Клиент передаёт значение как query-параметр
                `country_codes`.
            region_code: Целочисленный код региона из справочника СДЭК.
            kladr_region_code: Код КЛАДР региона. См. секцию Deprecated выше.
            fias_region_guid: UUID региона ФИАС. См. секцию Deprecated выше.
            kladr_code: Код КЛАДР населённого пункта.
            fias_guid: UUID населённого пункта ФИАС.
            postal_code: Почтовый индекс населённого пункта.
            code: Целочисленный код населённого пункта СДЭК.
            city: Полное название населённого пункта: требуется точное совпадение.
            size: Размер страницы, по умолчанию 1000. По документации обязателен, если указан `page`. None исключает
                поле из запроса.
            page: Номер страницы, начиная с 0. По умолчанию 0. None исключает поле из запроса.
            lang: Язык локализации ответа. Текущая спецификация метода не перечисляет допустимые значения.
            payment_limit: Ограничение суммы наложенного платежа, допускается дробное число. Специальные значения: -1
                - без ограничения, 0 - наложенный платёж не принимается.
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Декодированный JSON (список при успешном ответе), при `raise_errors=False` возможен словарь с ошибкой,
            а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        if kladr_region_code is not None:
            warnings.warn(
                "get_cities: `kladr_region_code` is absent from the current API v2 specification for this "
                "method; support is unconfirmed and the parameter will be removed in 3.0.0",
                DeprecationWarning,
                stacklevel=2,
            )

        if fias_region_guid is not None:
            warnings.warn(
                "get_cities: `fias_region_guid` is deprecated by the CDEK API specification and may return "
                "stale values",
                DeprecationWarning,
                stacklevel=2,
            )

        complete_data = drop_none(
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

        response = self.send(
            self.RESOURCE_CITIES, method="get", params=complete_data, raise_errors=raise_errors, **kwargs
        )

        if not origin_response:
            response = response.json()

        return response

    def get_all_cities(self, **kwargs) -> Iterator[dict]:
        """
        Iterate over all cities

        Обход начинается со страницы 0 и заканчивается на первом пустом списке. Переданные `page` и `origin_response`
        заменяются на 0 и False.

        Оставляйте `raise_errors=True`: обход ожидает список, а JSON-ошибка, возвращённая при отключённой проверке,
        не является страницей справочника.

        Args:
            **kwargs: Фильтры, размер страницы и HTTP-настройки для
                [`get_cities`][gocream_pycdek.client.CdekClient.get_cities].

        Yields:
            dict: Данные одного элемента справочника городов.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        request_kwargs = kwargs.copy()
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
    ) -> dict | Response:
        """
        Request receipt

        Создаёт запрос на формирование квитанции. Ответ не означает, что файл уже готов.

        https://apidoc.cdek.ru/#tag/print/operation/waybillPrint

        Args:
            orders: Список заказов для печати. В каждом элементе нужен `order_uuid` (UUID заказа) либо `cdek_number`
                (номер заказа СДЭК). Каждое поле обязательно при отсутствии другого.
            copy_count: Число копий квитанции на листе. По умолчанию на стороне API - 2. Рекомендуется не менее двух
                экземпляров: один для груза, другой для отправителя.
            form_type: Форма квитанции, передаваемая в поле `type`. По умолчанию - русская. Допустимы `tpl_china`,
                `tpl_armenia`, `tpl_russia`, `tpl_english`, `tpl_italian`, `tpl_korean`, `tpl_latvian`,
                `tpl_lithuanian`, `tpl_german`, `tpl_turkish`, `tpl_czech`, `tpl_thailand`, `tpl_invoice`.
            origin_response: Вернуть исходный HTTP-ответ вместо `entity`. По умолчанию False. Используйте True вместе
                с `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть,
                включая `raise_errors` и `timeout`.

        Returns:
            Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        complete_data = drop_none(
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
    ) -> dict | Response:
        """
        Request barcode

        Создаёт запрос на формирование штрихкодов. Ответ не означает, что файл уже готов.

        https://apidoc.cdek.ru/#tag/print/operation/barcodePrint

        Args:
            orders: Список заказов для печати. В каждом элементе нужен `order_uuid` (UUID заказа) либо `cdek_number`
                (номер заказа СДЭК). Каждое поле обязательно при отсутствии другого.
            copy_count: Число копий штрихкода. По умолчанию на стороне API - 1.
            format_type: Формат печати: `A4`, `A5`, `A6` или `A7` (латинская A). По умолчанию на стороне API - `A4`.
                Передаётся в поле `format`.
            lang: Язык печатной формы: `RUS` (русский) или `ENG` (английский), в формате ISO 639-3.
            origin_response: Вернуть исходный HTTP-ответ вместо `entity`. По умолчанию False. Используйте True вместе
                с `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть,
                включая `raise_errors` и `timeout`.

        Returns:
            Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        complete_data = drop_none(
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

    def get_receipt(self, uuid: str, origin_response: bool = False, **kwargs) -> dict | Response:
        """
        Get receipt information

        Возвращает сведения о формировании квитанции. Готовый файл можно скачать по ссылке `url` через
        [`download`][gocream_pycdek.client.CdekClient.download].

        https://apidoc.cdek.ru/#tag/print/operation/waybillGet

        Args:
            uuid: UUID задания на формирование печатной формы, возвращённый при её создании. Передаётся в пути
                запроса. UUID заказа здесь не используется.
            origin_response: Вернуть исходный HTTP-ответ вместо `entity`. По умолчанию False. Используйте True вместе
                с `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть,
                включая `raise_errors` и `timeout`.

        Returns:
            Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(f"{self.RESOURCE_RECEIPT}/{uuid}", method="get", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def get_barcode(self, uuid: str, origin_response: bool = False, **kwargs) -> dict | Response:
        """
        Get barcode information

        Возвращает сведения о формировании штрихкодов. Готовый файл можно скачать по ссылке `url` через
        [`download`][gocream_pycdek.client.CdekClient.download].

        https://apidoc.cdek.ru/#tag/print/operation/barcodeGet

        Args:
            uuid: UUID задания на формирование печатной формы, возвращённый при её создании. Передаётся в пути
                запроса. UUID заказа здесь не используется.
            origin_response: Вернуть исходный HTTP-ответ вместо `entity`. По умолчанию False. Используйте True вместе
                с `raise_errors=False`, если в ответе ошибки нет `entity`.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть, включая `raise_errors`
                и `timeout`.

        Returns:
            Информация из `entity`, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(f"{self.RESOURCE_BARCODE}/{uuid}", method="get", **kwargs)

        if not origin_response:
            response = response.json()["entity"]

        return response

    def download(self, url: str, origin_response: bool = False, **kwargs) -> BytesIO | Response:
        """
        Download document

        [Квитанция](https://apidoc.cdek.ru/#tag/print/operation/waybillDownload) и
        [штрихкоды](https://apidoc.cdek.ru/#tag/print/operation/barcodeDownload).

        Args:
            url: Ссылка `url` из ответа о готовой печатной форме. Документация описывает скачивание квитанции по
                `/v2/print/orders/{uuid}.pdf`, штрихкодов - по `/v2/print/barcodes/{uuid}.pdf`, где `uuid` относится к
                печатной форме. Абсолютную ссылку передавайте строкой.
            origin_response: Вернуть исходный HTTP-ответ вместо `BytesIO`. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть, включая `raise_errors`
                и `timeout`.

        Returns:
            Файл в памяти с указателем в начале, готовый к чтению.
            При `origin_response=True` - исходный HTTP-ответ.
            При `raise_errors=False` содержимое ответа возвращается даже при HTTP-ошибке.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(url, method="get", **kwargs)

        if origin_response:
            return response

        return BytesIO(response.content)

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
    ) -> dict | Response:
        """
        Calculate shipping cost with the legacy API

        Метод отсутствует в текущей спецификации API v2. Описания ниже отражают
        legacy-интерфейс клиента и не являются контрактом `calculator_tariff`.

        Deprecated:
            2.0.0: Используйте [`calculator_tariff`][gocream_pycdek.client.CdekClient.calculator_tariff]. Метод будет
                удалён в 3.0.0. Параметры нового калькулятора отличаются, поэтому вызов нужно адаптировать, а не просто
                переименовать.

        Args:
            goods (dict): Габариты груза: `weight` в килограммах, `length`, `width`, `height` в сантиметрах, `volume`
                в кубических метрах.
            version (str): Версия legacy-запроса. По умолчанию "1.0".
            auth_login (str, optional): Не используется. Сохранён для совместимости. При `auth=True` логин берётся из
                `client_id` клиента.
            secure (str, optional): Не используется. Сохранён для совместимости. При `auth=True` подпись вычисляется
                из секрета клиента и даты.
            date_execute (str, optional): Дата отправки в формате `yyyy-MM-dd`. При `auth=True` и отсутствии даты
                используется текущая локальная дата. Объект `datetime.date` не сериализуется в JSON.
            lang (str, optional): Язык ответа.
            sender_country_code (str, optional): Код страны отправителя.
            receiver_country_code (str, optional): Код страны получателя.
            sender_city_id (int, optional): Код города отправителя СДЭК.
            sender_city (str, optional): Название города отправителя.
            sender_city_post_code (str, optional): Почтовый индекс отправителя.
            receiver_city_id (int, optional): Код города получателя СДЭК.
            receiver_city_post_code (str, optional): Почтовый индекс получателя.
            receiver_city (str, optional): Название города получателя.
            sender_longitude (float, optional): Долгота отправителя.
            receiver_longitude (float, optional): Долгота получателя.
            sender_latitude (float, optional): Широта отправителя.
            receiver_latitude (float, optional): Широта получателя.
            tariff_id (int, optional): Код тарифа legacy-калькулятора.
            tariff_list (list, optional): Тарифы с полями `priority`, `id` и `mode_id`.
            services (dict, optional): Дополнительные услуги legacy-калькулятора.
            auth (bool): Добавить `authLogin` и `secure` из учётных данных клиента. По умолчанию False. Не управляет
                HTTP-заголовками в `send`.
            raise_errors (bool): Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response (bool): Вернуть исходный HTTP-ответ вместо JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Декодированный JSON, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekNoAuthClientException: При `auth=True` не заданы учётные данные клиента.
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        warnings.warn(
            "get_shipping_cost is deprecated and will be removed in 3.0.0; use calculator_tariff instead",
            DeprecationWarning,
            stacklevel=2,
        )

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
        tariff_code: int,
        from_location: dict,
        to_location: dict,
        packages: list[dict],
        *,
        contract_type: ContractType | int,
        date: str | None = None,
        currency: int | None = None,
        services: list[dict] | None = None,
        origin_response: bool = False,
        **kwargs,
    ) -> dict | Response:
        """
        Calculate shipping cost by tariff code

        https://apidoc.cdek.ru/#tag/calculator/operation/tariff

        Args:
            tariff_code: Код тарифа СДЭК, обязательный для расчёта по конкретному тарифу.
            from_location: Населённый пункт отправления. Поля: `code` (код СДЭК), `postal_code`, `country_code` (ISO
                3166-1 alpha-2, по умолчанию `RU`), `city`, `address`, `longitude`, `latitude`, `contragent_type`
                (`LEGAL_ENTITY` или `INDIVIDUAL`).
            to_location: Населённый пункт получения с теми же полями, что и `from_location`. Структура обязательна для
                расчёта.
            packages: Список мест. У каждой упаковки обязателен `weight` в граммах. `length`, `width`, `height`
                задаются в сантиметрах.
            contract_type: Тип заказа: `1` - интернет-магазин, `2` - доставка. API использует 1 по умолчанию, но
                клиент требует передать аргумент явно. Значение отправляется в поле `type`.
            date: Дата и время планируемой передачи заказа в формате `yyyy-MM-dd'T'HH:mm:ssZ`, например
                `2025-03-24T14:15:22+0700`. При отсутствии API использует текущую дату и время.
            currency: Числовой код валюты из приложения 14 "Код валюты для методов расчета стоимости". По умолчанию -
                валюта договора.
            services: Список дополнительных услуг: `code` - код услуги, `parameter` - её параметр. Например, для
                `INSURANCE` это объявленная стоимость, для `SMS` - телефон, для упаковки - количество или длина в
                зависимости от услуги.
            origin_response: Вернуть исходный HTTP-ответ вместо JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть, включая `raise_errors`
                и `timeout`.

        Returns:
            Полный JSON-ответ расчёта, а при `origin_response=True` - исходный HTTP-ответ.

        Raises:
            ValueError: Неизвестный тип заказа.
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        kwargs["data"] = drop_none(
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

    def subscribe(
        self, url: str, type: str, raise_errors: bool = True, origin_response: bool = False, **kwargs
    ) -> dict | Response:
        """
        Create webhook subscription

        https://apidoc.cdek.ru/#tag/webhook/operation/createWebhook

        Args:
            url: URL обработчика, на который СДЭК отправляет события.
            type: Тип вебхука: `ORDER_STATUS`, `ORDER_MODIFIED`, `PRINT_FORM`, `RECEIPT`, `DOWNLOAD_PHOTO`,
                `PREALERT_CLOSED`, `ACCOMPANYING_WAYBILL`, `OFFICE_AVAILABILITY`, `DELIV_PROBLEM`, `DELIV_AGREEMENT`
                или `COURIER_INFO`. Повторный вызов с уже существующим типом создаёт ещё одну подписку.
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Полный JSON-ответ о создании подписки, включая служебные сведения.
            При `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        complete_data = drop_none(
            {
                "url": url,
                "type": type,
            }
        )

        response = self.send(
            self.RESOURCE_SUBSCRIPTION, method="post", data=complete_data, raise_errors=raise_errors, **kwargs
        )

        if not origin_response:
            response = response.json()

        return response

    def subscribe_info(
        self, raise_errors: bool = True, origin_response: bool = False, **kwargs
    ) -> list[dict] | dict | Response:
        """
        List webhook subscriptions

        https://apidoc.cdek.ru/#tag/webhook/operation/getAll

        Args:
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Список подписок при успешном ответе. При `raise_errors=False` возможен словарь с ошибкой.
            При `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(self.RESOURCE_SUBSCRIPTION, method="get", raise_errors=raise_errors, **kwargs)

        if not origin_response:
            response = response.json()

        return response

    def subscribe_info_by_uuid(
        self, uuid: str, raise_errors: bool = True, origin_response: bool = False, **kwargs
    ) -> dict | Response:
        """
        Get webhook subscription

        https://apidoc.cdek.ru/#tag/webhook/operation/getById

        Args:
            uuid: Идентификатор вебхука, сведения о котором необходимо получить. Передаётся в пути запроса.
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Полный JSON-ответ со сведениями о подписке, включая `entity` и `requests`. При `origin_response=True`
            - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(f"{self.RESOURCE_SUBSCRIPTION}/{uuid}", method="get", raise_errors=raise_errors, **kwargs)

        if not origin_response:
            response = response.json()

        return response

    def subscribe_delete(
        self, uuid: str, raise_errors: bool = True, origin_response: bool = False, **kwargs
    ) -> dict | Response:
        """
        Delete webhook subscription

        https://apidoc.cdek.ru/#tag/webhook/operation/deleteById

        Args:
            uuid: Идентификатор вебхука, который необходимо удалить. Передаётся в пути запроса.
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Полный JSON-ответ на запрос удаления подписки. При `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        response = self.send(
            f"{self.RESOURCE_SUBSCRIPTION}/{uuid}", method="delete", raise_errors=raise_errors, **kwargs
        )

        if not origin_response:
            response = response.json()

        return response

    def get_deliverypoints(
        self,
        postal_code: str | int | None = None,
        city_code: int | None = None,
        type: str | None = None,
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
        **kwargs,
    ) -> list[dict] | dict | Response:
        """
        Request delivery points

        https://apidoc.cdek.ru/#tag/delivery_point/operation/search

        Args:
            postal_code: Почтовый индекс города, для которого запрашивается список офисов. Строка сохраняет ведущие
                нули.
            city_code: Код города по справочнику СДЭК.
            type: Тип офиса: `POSTAMAT`, `PVZ` или `ALL`. При отсутствии фильтра API использует `ALL`.
            country_code: Код страны в формате ISO 3166-1 alpha-2.
            region_code: Код региона по справочнику СДЭК.
            have_cashless: Наличие терминала оплаты. True — только офисы с этим признаком, False — только без него,
                None — фильтр не применяется.
            have_cash: Приём наличных. True — только офисы с этим признаком, False — только без него, None — фильтр
                не применяется.
            allowed_cod: Возможность наложенного платежа. True — только офисы с этим признаком, False — только без
                него, None — фильтр не применяется.
            is_dressing_room: Наличие примерочной. True — только офисы с этим признаком, False — только без него,
                None — фильтр не применяется.
            weight_max: Фильтр максимального принимаемого веса в килограммах, не меньше 0. Положительное значение
                выбирает офисы, принимающие такой вес. 0 исключает офисы с нулевым ограничением. Отсутствие поля не
                ограничивает выборку по весу.
            weight_min: Фильтр минимального принимаемого веса в килограммах, не меньше 0. Выбирает офисы, чей
                минимальный принимаемый вес не превышает указанного.
            lang: Локализация описания офиса. По умолчанию на стороне API - `rus`.
            take_only: Офис является только пунктом выдачи. True — только офисы с этим признаком, False — только без
                него, None — фильтр не применяется.
            is_handout: Офис является пунктом выдачи. True — только офисы с этим признаком, False — только без него,
                None — фильтр не применяется.
            raise_errors: Вызывать исключение при ошибочном HTTP-статусе. По умолчанию True.
            origin_response: Вернуть исходный HTTP-ответ вместо декодированного JSON. По умолчанию False.
            **kwargs: Передаются в [`send`][gocream_pycdek.client.CdekClient.send] как есть.

        Returns:
            Список пунктов выдачи при успешном ответе. При `raise_errors=False` возможен словарь с ошибкой, а при
            `origin_response=True` - исходный HTTP-ответ.

        Raises:
            CdekRequestException: Ответ с ошибочным HTTP-статусом при `raise_errors=True`.
        """

        complete_data = drop_none(
            {
                "postal_code": postal_code,
                "city_code": city_code,
                "type": type,
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
            self.RESOURCE_DELIVERYPOINTS, method="get", params=complete_data, raise_errors=raise_errors, **kwargs
        )

        if not origin_response:
            response = response.json()

        return response
