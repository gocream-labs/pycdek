# -*- coding: utf-8 -*-

from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
import datetime as dt
import json
import logging

import jwt
import requests

from pycdek.utils import clear_dict, get_secure


logger = logging.getLogger("pycdek")


class CDEKApiClient:
    """
    Client for cdek api
    """
    PRODUCTION_API_URL = 'api.cdek.ru/v2/'
    DEVELOPMENT_API_URL = 'api.edu.cdek.ru/v2/'

    CONTRACT_TYPE_SHOP = 'shop'
    CONTRACT_TYPE_DELIVERY = 'delivery'

    RESOURCE_ORDER = 'orders'
    RESOURCE_INTAKES = 'intakes'
    RESOURCE_REGIONS = 'location/regions'
    RESOURCE_CITIES = 'location/cities'
    RESOURCE_INVOICE = 'print/orders'
    RESOURCE_CALCULATOR_URL = 'http://api.cdek.ru/calculator/calculate_price_by_json.php'

    def __init__(self, id, secret, is_shop, production=True):
        """
        Args:
            id (str): cdek client_id
            secret (str): cdek client_secret
            is_shop (bool): cdek contract type
            production (bool, optional): prodaction or development api use. Default True.
        """

        self.id = id
        self.secret = secret
        self.contract_type = self.CONTRACT_TYPE_SHOP if is_shop else self.CONTRACT_TYPE_DELIVERY
        self.production = production

    _token = None
    _token_exp = None

    @property
    def token(self):
        """
        request token if needed and return token
        """

        # for safe add 5 minutes
        now = dt.timedelta(minutes=5) + dt.datetime.now()
        if not self._token or self._token_exp <= now:
            # token not getted or expired -> response
            response = self.authorization()
            self._token = response['access_token']
            token_data = jwt.decode(response['access_token'], verify=False)
            self._token_exp = dt.datetime.fromtimestamp(token_data['exp'])

        return self._token

    def authorization(self):
        """
        request jwt token for use in api requests
        """

        response = requests.post(self.get_url('oauth/token'), params={
            'grant_type': 'client_credentials',
            'client_id': self.id,
            'client_secret': self.secret,
        })
        json = response.json()

        token_type = json['token_type']
        assert token_type == 'bearer', f"CDEK return token type `{token_type}` that not supported."

        return json

    def get_url(self, resource):
        """
        make request url
        """

        if str(resource).startswith('http'):
            return resource

        api = self.PRODUCTION_API_URL if self.production else self.DEVELOPMENT_API_URL
        return f"http://{Path(api) / Path(resource)}"

    def get_headers(self):
        """
        make headers for requests
        """

        return {
            'Authorization': f'Bearer {self.token}'
        }

    def send(self, resource, data=None, method='get', raise_errors=True, **kwargs):
        """
        Send request and add token to headers

        Args:
            resource (str|Path): resource path
            data (dict, optional): dictionary of request data used in json. Default to None.
            method (str, optional): request method (default: get)
            raise_errors (bool, optional): raise errors? (default: True)

        Returns:
            dict: request returned data
        """

        request_kwargs = {
            'headers': self.get_headers(),
            'json': data,
        }
        request_kwargs.update(kwargs)

        if method == 'get':
            response = requests.get(self.get_url(resource), **request_kwargs)

        elif method == 'post':
            response = requests.post(self.get_url(resource), **request_kwargs)

        elif method == 'delete':
            response = requests.delete(self.get_url(resource), **request_kwargs)

        if raise_errors:
            response.raise_for_status()

        return response

    def registrate_order(
            self,
            tariff_code,
            recipient,
            from_location,
            to_location,
            packages,
            number=None,
            comment=None,
            shipment_point=None,
            delivery_point=None,
            items_cost_currency=None,
            date_invoice=None,
            shipper_name=None,
            shipper_address=None,
            # наложенный платёж,
            recipient_currency=None,
            delivery_recipient_cost=None,
            delivery_recipient_cost_adv=None,
            sender=None,
            seller=None,
            services=None,
            raise_errors=True,
            origin_response=False,
        ):
        """
        Registrate order

        Args:
            tariff_code (int): Код тарифа `tarrifs`_.
            recipient (dict): Получатель:
                name (str): ФИО контактного лица
                tin (str): ИНН
                phones (list of dict): Список телефонов:
                    number (str): Номер телефона. Должен передаваться в международном формате: код страны (для России +7) и сам номер (10 и более цифр)
                    additional (str, optional): Дополнительная информация (доп. номер)
                company (str, optional): Название компании
                passport_series (str, optional): Серия паспорта
                passport_number (str, optional): Номер паспорта
                passport_date_of_issue (str, optional): Дата выдачи паспорта в формате 'yyyy-MM-dd'
                passport_organization (str, optional): Орган выдачи паспорта
                passport_date_of_birth (date, optional): Дата рождения в формате 'yyyy-MM-dd'
                email (str, optional): Эл. адрес
            from_location (dict): Адрес отправления:
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
            to_location (dict): Адрес получения:
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
            packages (dict): Список информации по местам (упаковкам)
                number (str): Номер упаковки (можно использовать порядковый номер упаковки заказа или номер заказа), уникален в пределах заказа. Идентификатор заказа в ИС Клиента
                weight (int): Общий вес (в граммах)
                length (int, optioanl): Габариты упаковки. Длина (в сантиметрах)
                width (int, optioanl): Габариты упаковки. Ширина (в сантиметрах)
                height (int, optioanl): Габариты упаковки. Высота (в сантиметрах)
                comment (str, optioanl): Комментарий к упаковке
                items (list of dict, optioanl): Позиции товаров в упаковке:
                    name (str): Наименование товара (может также содержать описание товара: размер, цвет)
                    ware_key (str): Идентификатор/артикул товара
                    payment (dict): Оплата за товар при получении (за единицу товара в указанной валюте, значение >=0) — наложенный платеж, в случае предоплаты значение = 0:
                        value (float): Сумма дополнительного сбора
                        vat_sum (float, optional): Сумма НДС
                        vat_rate (int, optional): Ставка НДС (значение - 0, 10, 18, 20 и т.п. , null - нет НДС)
                    cost (float): Объявленная стоимость товара (за единицу товара в указанной валюте, значение >=0). С данного значения рассчитывается страховка
                    weight (int): Вес (за единицу товара, в граммах)
                    weight_gross (int, optional): Вес брутто
                    amount (int): Количество единиц товара (в штуках)
                    name_i18n (str, optional): Наименование на иностранном языке
                    brand (str, optional): Бренд на иностранном языке
                    country_code (str, optional): Код страны в формате  ISO_3166-1_alpha-2
                    material (str, optional): Код материала
                    wifi_gsm (bool, optional): Содержит wifi/gsm
                    url (str, optional): Ссылка на сайт интернет-магазина с описанием товара
            number (str, optional): Номер заказа в ИС Клиента (если не передан, будет присвоен номер заказа в ИС СДЭК - uuid). Только для заказов "интернет-магазин".
            comment (str, optional): Комментарий к заказу.
            shipment_point (str, optional): Код ПВЗ СДЭК, на который будет производится забор отправления, либо самостоятельный привоз клиентом.
            delivery_point (str, optional): Код ПВЗ СДЭК, на который будет доставлена посылка.
            items_cost_currency (str, optional): Код валюты объявленной стоимости заказа всех вложений `currency`_.
            date_invoice (date, optional): Дата инвойса.
            shipper_name (str, optional): Грузоотправитель.
            shipper_address (str, optional): Адрес грузоотправителя.
            recipient_currency (str, optional): Код валюты наложенного платежа: доп. сбора за доставку и оплаты за товар с получателя `currency`_.
            delivery_recipient_cost (dict, optional): Доп. сбор за доставку, которую ИМ берет с получателя. Валюта сбора должна совпадать с валютой наложенного платежа:
                value (float): Сумма дополнительного сбора
                vat_sum (float, optional): Сумма НДС
                vat_rate (int, optional): Ставка НДС (значение - 0, 10, 18, 20 и т.п. , null - нет НДС)
            delivery_recipient_cost_adv (dict, optional): Доп. сбор за доставку (которую ИМ берет с получателя) в зависимости от суммы заказа:
                threshold (int): Порог стоимости товара (действует по условию меньше или равно) в целых единицах валюты
                sum (float): Доп. сбор за доставку товаров, общая стоимость которых попадает в интервал
                vat_sum (float, optional): Сумма НДС, включённая в доп. сбор за доставку
                vat_rate (int, optional): Ставка НДС (значение - 0, 10, 18, 20 и т.п. , null - нет НДС)
            sender (dict, optional): Отправитель:
                company (str, optional): Название компании.
                name (str, optional): ФИО контактного лица.
                email (str, optional): Эл. адрес.
                phones (list of `dict`, optional): Список телефонов:
                    number (str): Номер телефона. Должен передаваться в международном формате: код страны (для России +7) и сам номер (10 и более цифр).
                    additional (str, optional): Дополнительная информация (доп. номер).
            seller (dict, optional): Реквизиты реального продавца:
                name (str, optional): Наименование истинного продавца.
                inn (str, optional): ИНН истинного продавца.
                phone (str, optional): Телефон истинного продавца.
                ownership_form (int, optional): Код формы собственности `ownership form`_.
                address (str, optional): Адрес истинного продавца. Используется при печати инвойсов для отображения адреса настоящего продавца товара, либо торгового названия.
            services (dict, optional): Дополнительные услуги:
                code (int): Тип дополнительной услуги `extra services`_.
                parameter (int, optional): Параметр дополнительной услуги:
                    * количество упаковок для услуги "Упаковка 1" (для всех типов заказа)
                    * объявленная стоимость заказа для услуги "Страхование" (только для заказов с типом "доставка")
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: Order dict

        .. _documentation:
            https://confluence.cdek.ru/pages/viewpage.action?pageId=29923926
        .. _tarrifs:
            https://confluence.cdek.ru/pages/viewpage.action?pageId=29923926#id-Регистрациязаказа-TariffПриложение1.ТарифыСДЭК
        .. _currency:
            https://confluence.cdek.ru/pages/viewpage.action?pageId=29923926#id-Регистрациязаказа-CurrencyПриложение2.Валюта
        .. _ownership form:
            https://confluence.cdek.ru/pages/viewpage.action?pageId=29923926#id-Регистрациязаказа-OwnershipПриложение3.Формасобственности
        .. _extra services:
            https://confluence.cdek.ru/pages/viewpage.action?pageId=29923926#id-Регистрациязаказа-ServicesПриложение4.Дополнительныеуслуги
        """

        complete_data = clear_dict({
            'type': 1 if self.contract_type == self.CONTRACT_TYPE_SHOP else 2,
            'tariff_code': tariff_code,
            'recipient': recipient,
            'from_location': from_location,
            'to_location': to_location,
            'packages': packages,
            'number': number,
            'comment': comment,
            'shipment_point': shipment_point,
            'delivery_point': delivery_point,
            'items_cost_currency': items_cost_currency,
            'date_invoice': date_invoice,
            'shipper_name': shipper_name,
            'shipper_address': shipper_address,
            'recipient_currency': recipient_currency,
            'delivery_recipient_cost': delivery_recipient_cost,
            'delivery_recipient_cost_adv': delivery_recipient_cost_adv,
            'sender': sender,
            'seller': seller,
            'services': services,
        })

        response = self.send(
            self.RESOURCE_ORDER,
            complete_data,
            method='post',
            raise_errors=raise_errors,
        )

        if not origin_response:
            response = response.json()['entity']

        return response

    def get_order(self, uuid, raise_errors=True, origin_response=False):
        """
        Get order info

        Args:
            uuid (str): order cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: order info
        """

        response = self.send(Path(self.RESOURCE_ORDER) / Path(uuid), raise_errors=raise_errors)

        if not origin_response:
            response = response.json()['entity']

        return response

    def remove_order(self, uuid, raise_errors=True):
        """
        Remove order

        Args:
            uuid (str): order cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)

        Returns:
            dict: deleted order info
        """

        return self.send(
            Path(self.RESOURCE_ORDER) / Path(uuid),
            method='delete',
            raise_errors=raise_errors
        )

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

        Args:
            intake_date (str): Дата ожидания курьера в формате (yyyy-MM-dd)
            intake_time_from (time): Время начала ожидания курьера
            intake_time_to (time): Время окончания ожидания курьера
            order_uuid (str, optional): Идентификатор заказа в ИС СДЭК (UUID)
            lunch_time_from (time, optional): Время начала обеда, должно входить в диапозон [intake_time_to;intake_time_to]
            lunch_time_to (time, optional): Время окончания обеда, должно входить в диапозон [intake_time_to;intake_time_to]
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

        complete_data = clear_dict({
            'intake_date': intake_date,
            'intake_time_from': intake_time_from,
            'intake_time_to': intake_time_to,
            'order_uuid': order_uuid,
            'lunch_time_from': lunch_time_from,
            'lunch_time_to': lunch_time_to,
            'name': name,
            'cdek_number': cdek_number,
            'weight': weight,
            'length': length,
            'width': width,
            'height': height,
            'comment': comment,
            'sender': sender,
            'from_location': from_location,
            'need_call': need_call,
        })

        response = self.send(
            self.RESOURCE_INTAKES,
            complete_data,
            method='post',
            raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()['entity']

        return response

    def get_intakes(self, uuid, raise_errors=True, origin_response=False):
        """
        Get intakes info

        Args:
            uuid (str): intakes cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: intakes info
        """

        response = self.send(
            Path(self.RESOURCE_INTAKES) / Path(uuid),
            raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()['entity']

        return response

    def remove_intakes(self, uuid, raise_errors=True):
        """
        Remove intakes

        Args:
            uuid (str): intakes cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)

        Returns:
            dict: deleted intakes info
        """

        return self.send(
            Path(self.RESOURCE_INTAKES) / Path(uuid),
            method='delete',
            raise_errors=raise_errors
        )

    def get_regions(
        self,
        country_codes: Optional[List[str]] = None,
        region_code: Optional[str] = None,
        kladr_region_code: Optional[str] = None,
        fias_region_guid: Optional[str] = None,
        size: Optional[int] = 1000,
        page: Optional[int] = 0,
        lang: Optional[str] = None,
        raise_errors: Optional[bool] = True,
        origin_response: Optional[bool] = False,
    ) -> List:
        """
        Request regions

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


        https://confluence.cdek.ru/pages/viewpage.action?pageId=33829418
        """

        complete_data = clear_dict({
            'country_codes': country_codes,
            'region_code': region_code,
            'kladr_region_code': kladr_region_code,
            'fias_region_guid': fias_region_guid,
            'size': size,
            'page': page,
            'lang': lang,
        })

        response = self.send(
            Path(self.RESOURCE_REGIONS),
            complete_data,
            raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()

        return response

    def get_all_regions(self, **kwargs):
        request_kwargs = deepcopy(kwargs)
        request_kwargs['page'] = 0
        request_kwargs['origin_response'] = False

        while True:
            regions = self.get_regions(**request_kwargs)

            if len(regions) == 0:
                break

            for region in regions:
                yield region

            request_kwargs['page'] += 1

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

        complete_data = clear_dict({
            'country_codes': country_codes,
            'region_code': region_code,
            'kladr_region_code': kladr_region_code,
            'fias_region_guid': fias_region_guid,
            'kladr_code': kladr_code,
            'fias_guid': fias_guid,
            'postal_code': postal_code,
            'code': code,
            'city': city,
            'page': page,
            'size': size,
            'lang': lang,
            'payment_limit': payment_limit,
        })

        response = self.send(
            Path(self.RESOURCE_CITIES),
            complete_data,
            raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()

        return response

    def get_all_cities(self, **kwargs):
        request_kwargs = deepcopy(kwargs)
        request_kwargs['page'] = 0
        request_kwargs['origin_response'] = False

        while True:
            cities = self.get_cities(**request_kwargs)

            if len(cities) == 0:
                break

            for city in cities:
                yield city

            request_kwargs['page'] += 1

    def request_invoice(self, uuids, copy_count=2, raise_errors=True, origin_response=False):
        """
        Request for the receipt of an order

        Args:
            uuids (str[]): cdek orders uuids
            copy_count (integer, optional): count of invoice on page (default: 2)
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: requested invoice dict

        https://confluence.cdek.ru/pages/viewpage.action?pageId=36967276
        """

        complete_data = clear_dict({
            'orders': [{'order_uuid': uuid} for uuid in uuids],
            'copy_count': copy_count,
        })

        response = self.send(
            self.RESOURCE_INVOICE,
            complete_data,
            method='post',
            raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()['entity']

        return response

    def get_invoice(self, uuid, raise_errors=True, origin_response=False):
        """
        Get link to invoice

        Args:
            uuid (str): intakes cdek uuid
            raise_errors (bool, optional): raise errors? (default: True)
            origin_response (bool, optional): return original response or only entity? (default: False)

        Returns:
            dict: requested invoice dict

        https://confluence.cdek.ru/pages/viewpage.action?pageId=36967287
        """

        response = self.send(
            Path(self.RESOURCE_INVOICE) / Path(uuid),
            raise_errors=raise_errors
        )

        if not origin_response:
            response = response.json()['entity']

        return response

    def download(self, url):
        # response = self.send(url)
        # media = BytesIO()
        # media.write(response.content)
        # return media

        r = self.send(url, stream=True)
        if r.status_code == 200:
            with open('test.pdf', 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

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
    ):
        """
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
        sender_country_code (str, optional): Код страны отправителя в формате ISO_3166-1_alpha-2 (см. “Общероссийский классификатор стран мира”). По умолчанию - ru.
        receiver_country_code (str, optional): Код страны получателя в формате ISO_3166-1_alpha-2 (см. “Общероссийский классификатор стран мира”). По умолчанию - ru.
        sender_city_id (int, optional): Код города отправителя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
        sender_city (str, optional): Наименование города отправителя string  нет
        sender_city_post_code (int, optional): Индекс города отправителя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
        receiver_city_id (int, optional): Код города получателя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
        receiver_city_post_code (int, optional): Индекс города получателя из базы СДЭК (см. файл «City_XXX_YYYYMMDD.xls»)
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

        https://confluence.cdek.ru/pages/viewpage.action?pageId=15616129#id-Протоколобменаданными(v1.5)-4.14CalculatorКалькулятор
        """

        complete_data = clear_dict({
            'goods': goods,
            'version': version,
            'dateExecute': date_execute,
            'lang': lang,
            'senderCountryCode': sender_country_code,
            'receiverCountryCode': receiver_country_code,
            'senderCityId': sender_city_id,
            'senderCity': sender_city,
            'senderCityPostCode': sender_city_post_code,
            'receiverCityId': receiver_city_id,
            'receiverCityPostCode': receiver_city_post_code,
            'receiverCity': receiver_city,
            'senderLongitude': sender_longitude,
            'receiverLongitude': receiver_longitude,
            'senderLatitude': sender_latitude,
            'receiverLatitude': receiver_latitude,
            'tariffId': tariff_id,
            'tariffList': tariff_list,
            'services': services,
        })

        if auth:
            assert self.id and self.secret, "Has no provide auth information"

            today = dt.date.today().isoformat()
            if not 'dateExecute' in complete_data:
                complete_data['dateExecute'] = today

            complete_data['authLogin'] = self.id
            complete_data['secure'] = get_secure(self.secret, today)


        response = self.send(self.RESOURCE_CALCULATOR_URL, json=complete_data)

        if raise_errors:
            response.raise_for_status()

        if not origin_response:
            response = response.json()

        return response
