# -*- coding: utf-8 -*-

import datetime as dt
import logging

import jwt
import requests


logger = logging.getLogger("pycdek")



CONTRACT_TYPE_SHOP = 'shop'
CONTRACT_TYPE_DELIVERY = 'delivery'


class Client:
    """
    Client for cdek api
    """
    production_api_url = 'api.cdek.ru/v2/'
    development_api_url = 'api.edu.cdek.ru/v2/'

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
        self.contract_type = CONTRACT_TYPE_SHOP if is_shop else DEVELOPMENT_API_URL
        self.api_url = api_url

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
            self._token = response.json()['access_token']
            token_data = jwt.decode(response.json()['access_token'], verify=False)
            self._token_exp = dt.datetime.fromtimestamp(token_data['exp'])

        return self._token

    def authorization(self):
        """
        request jwt token for use in api requests
        """

        response = requests.post(self.get_url('oauth/token?parameters'), {
            'grant_type': 'client_credentials',
            'client_id': self.id,
            'client_secret': self.secret,
        })
        json = response.json()

        assert json['token_type'] != 'bearer', f"CDEK token type `{json['token_type']}` not support"

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

    def send(self, resource, data):
        """
        send request and add token to headers
        """

        return requests.post(self.get_url(resource), headers=self.get_headers()).json()

    def registrate_order(self, data, tariff_code=None, number=None, comment=None, shipment_point=None):
        """
        Registrate order

        Args:
            tariff_code (int): Код тарифа
            number (str, optional): Номер заказа в ИС Клиента (если не передан, будет присвоен номер заказа в ИС СДЭК - uuid). Только для заказов "интернет-магазин".
            comment (str, optional): Комментарий к заказу
            shipment_point (str, optional): Код ПВЗ СДЭК, на который будет производится забор отправления, либо самостоятельный привоз клиентом


        _documentation:: https://confluence.cdek.ru/pages/viewpage.action?pageId=29923926
        """

        # assert order.get('type'), "Order should not contain field `type`"
        # if self.contract_type == CONTRACT_TYPE_SHOP:
        # else:
        #     assert order.get('number'), "Contract type `Delivery` should not contain field `number`"

        # logger.info("registrate order in cdek")

        complete_data = {
            'type': 1 if self.contract_type == CONTRACT_TYPE_SHOP else 2,
        }

        return self.send('orders', complete_data)
