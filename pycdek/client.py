# -*- coding: utf-8 -*-

from pathlib import Path
import datetime as dt
import logging

import jwt
import requests

from pycdek.utils import clear_dict


logger = logging.getLogger("pycdek")


class CDEKApiClient:
    """
    Client for cdek api
    """
    production_api_url = 'api.cdek.ru/v2/'
    development_api_url = 'api.edu.cdek.ru/v2/'

    contract_type_shop = 'shop'
    contract_type_delivery = 'delivery'

    resourse_order = 'orders'

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
        self.contract_type = self.contract_type_shop if is_shop else self.contract_type_delivery
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

        response = requests.post(self.get_url('oauth/token'),{
            'grant_type': 'client_credentials',
            'client_id': self.id,
            'client_secret': self.secret,
        })
        json = response.json()

        assert json['token_type'] == 'bearer', f"CDEK return token type `{json['token_type']}` that not supported."

        return json

    def get_url(self, resource):
        """
        make request url
        """

        api = self.production_api_url if self.production else self.development_api_url
        return f"http://{Path(api) / Path(resource)}"

    def get_headers(self):
        """
        make headers for requests
        """

        return {
            'Authorization': f'Bearer {self.token}'
        }

    def send(self, resource, data=None, method='get'):
        """
        Send request and add token to headers

        Args:
            resource (str|Path): resource path
            data (dict, optional): dictionary of request data used in json. Default to None.

        Returns:
            dict: request returned data
        """

        kwargs = {
            'headers': self.get_headers(),
            'json': data,
        }

        if method == 'get':
            response = requests.get(self.get_url(resource), **kwargs)

        elif method == 'post':
            response = requests.post(self.get_url(resource), **kwargs)

        elif method == 'delete':
            response = requests.delete(self.get_url(resource), **kwargs)

        return response.json()

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
                    weight_gross (int, optional): Вес брутто:
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
            'type': 1 if self.contract_type == self.contract_type_shop else 2,
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

        return self.send(self.resourse_order, complete_data, method='post')

    def get_order(self, uuid):
        """
        Get order info

        Args:
            uuid (str): order cdek uuid

        Returns:
            dict: order info
        """

        return self.send(Path(self.resourse_order) / Path(uuid))
        # if self.contract_type == CONTRACT_TYPE_SHOP:
        # else:

    def remove_order(self, uuid):
        """
        Remove order

        Args:
            uuid (str): order cdek uuid

        Returns:
            dict: deleted order info
        """

        return self.send(Path(self.resourse_order) / Path(uuid), method='delete')

        return self.send('orders', complete_data)
