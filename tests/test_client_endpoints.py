"""Endpoint-level HTTP-контракты реализованных методов клиента."""

import json

import pytest
import responses
from requests import HTTPError


API_URL = "https://api.edu.cdek.ru/"
ORDER_UUID = "11111111-1111-4111-8111-111111111111"
INTAKE_UUID = "22222222-2222-4222-8222-222222222222"
RECEIPT_UUID = "33333333-3333-4333-8333-333333333333"
BARCODE_UUID = "44444444-4444-4444-8444-444444444444"
WEBHOOK_UUID = "55555555-5555-4555-8555-555555555551"
MISSING_WEBHOOK_UUID = "55555555-5555-4555-8555-555555555555"


def request_json():
    """Декодирует JSON-тело единственного HTTP-запроса теста."""
    return json.loads(responses.calls[0].request.body)


def order_data():
    """Возвращает валидные данные заказа из сценария сбора fixtures."""
    recipient = {"name": "Тестовый получатель", "phones": [{"number": "+70000000001"}]}
    packages = [
        {
            "number": "1",
            "weight": 100,
            "length": 10,
            "width": 10,
            "height": 10,
            "items": [
                {
                    "name": "Тестовый товар",
                    "ware_key": "fixture-item",
                    "payment": {"value": 0},
                    "cost": 100,
                    "weight": 100,
                    "amount": 1,
                }
            ],
        }
    ]
    return recipient, packages


@responses.activate
def test_register_order_endpoint(authorized_test_client, api_response):
    """Проверяет POST регистрации заказа."""
    payload = api_response("order_create")
    responses.add(responses.POST, f"{API_URL}v2/orders", json=payload, status=202)
    recipient, packages = order_data()

    result = authorized_test_client.registrate_order(
        136,
        recipient,
        packages,
        number="fixture-order-1",
        shipment_point="MSK65",
        delivery_point="NSK23",
    )

    assert result == payload["entity"]
    assert request_json() == {
        "type": 1,
        "tariff_code": 136,
        "recipient": recipient,
        "packages": packages,
        "number": "fixture-order-1",
        "shipment_point": "MSK65",
        "delivery_point": "NSK23",
    }


@pytest.mark.parametrize(
    ("identifier", "value"),
    [
        ("cdek_number", "1100000001"),
        ("im_number", "fixture-order-1"),
    ],
    ids=["cdek-number", "im-number"],
)
@responses.activate
def test_get_order_by_number_endpoint(authorized_test_client, api_response, identifier, value):
    """Проверяет GET заказа по query-параметру номера."""
    payload = api_response("order_get")
    responses.add(responses.GET, f"{API_URL}v2/orders", json=payload, status=200)

    result = authorized_test_client.get_order(**{identifier: value})

    assert result == payload["entity"]
    assert responses.calls[0].request.params == {identifier: value}


@responses.activate
def test_get_order_by_uuid_endpoint(authorized_test_client, api_response):
    """Проверяет GET заказа по UUID в URL."""
    payload = api_response("order_get")
    url = f"{API_URL}v2/orders/{ORDER_UUID}"
    responses.add(responses.GET, url, json=payload, status=200)

    result = authorized_test_client.get_order(uuid=ORDER_UUID)

    assert result == payload["entity"]
    assert responses.calls[0].request.url == url


@responses.activate
def test_remove_order_endpoint(authorized_test_client, api_response):
    """Проверяет DELETE заказа."""
    payload = api_response("order_delete")
    url = f"{API_URL}v2/orders/{ORDER_UUID}"
    responses.add(responses.DELETE, url, json=payload, status=202)

    result = authorized_test_client.remove_order(ORDER_UUID)

    assert result.json() == payload
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_register_intake_endpoint(authorized_test_client, api_response):
    """Проверяет POST регистрации заявки на забор."""
    payload = api_response("intake_create")
    responses.add(responses.POST, f"{API_URL}v2/intakes", json=payload, status=202)
    sender = {"name": "Тестовый отправитель", "phones": [{"number": "+70000000000"}]}
    location = {"code": 44, "country_code": "RU", "address": "Тестовый адрес отправителя"}

    result = authorized_test_client.registrate_intakes(
        "2026-08-03",
        "10:00",
        "18:00",
        name="Тестовая посылка",
        weight=100,
        length=10,
        width=10,
        height=10,
        sender=sender,
        from_location=location,
    )

    assert result == payload["entity"]
    assert request_json() == {
        "intake_date": "2026-08-03",
        "intake_time_from": "10:00",
        "intake_time_to": "18:00",
        "name": "Тестовая посылка",
        "weight": 100,
        "length": 10,
        "width": 10,
        "height": 10,
        "sender": sender,
        "from_location": location,
    }


@responses.activate
def test_get_intake_endpoint(authorized_test_client, api_response):
    """Проверяет GET заявки на забор."""
    payload = api_response("intake_get")
    url = f"{API_URL}v2/intakes/{INTAKE_UUID}"
    responses.add(responses.GET, url, json=payload, status=200)

    result = authorized_test_client.get_intakes(INTAKE_UUID)

    assert result == payload["entity"]
    assert responses.calls[0].request.url == url


@responses.activate
def test_remove_intake_endpoint(authorized_test_client, api_response):
    """Проверяет DELETE заявки на забор."""
    payload = api_response("intake_delete")
    responses.add(responses.DELETE, f"{API_URL}v2/intakes/{INTAKE_UUID}", json=payload, status=202)

    result = authorized_test_client.remove_intakes(INTAKE_UUID)

    assert result.json() == payload
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_get_regions_endpoint(authorized_test_client, api_response):
    """Проверяет GET справочника регионов."""
    payload = api_response("regions")
    responses.add(responses.GET, f"{API_URL}v2/location/regions", json=payload, status=200)

    result = authorized_test_client.get_regions(country_codes=["RU"], size=2, page=0)

    assert result == payload
    assert responses.calls[0].request.params == {"country_codes": "RU", "size": "2", "page": "0"}


@responses.activate
def test_get_cities_endpoint(authorized_test_client, api_response):
    """Проверяет GET справочника городов."""
    payload = api_response("cities")
    responses.add(responses.GET, f"{API_URL}v2/location/cities", json=payload, status=200)

    result = authorized_test_client.get_cities(city="Москва", size=2, page=0)

    assert result == payload
    assert responses.calls[0].request.params == {"city": "Москва", "page": "0", "size": "2"}


@responses.activate
def test_request_receipt_endpoint(authorized_test_client, api_response):
    """Проверяет POST запроса квитанции."""
    payload = api_response("receipt_create")
    responses.add(responses.POST, f"{API_URL}v2/print/orders", json=payload, status=202)
    orders = [{"order_uuid": ORDER_UUID}]

    result = authorized_test_client.request_receipt(orders, copy_count=2)

    assert result == payload["entity"]
    assert request_json() == {"orders": orders, "copy_count": 2}


@responses.activate
def test_get_receipt_endpoint(authorized_test_client, api_response):
    """Проверяет GET квитанции."""
    payload = api_response("receipt_get")
    url = f"{API_URL}v2/print/orders/{RECEIPT_UUID}"
    responses.add(responses.GET, url, json=payload, status=200)

    result = authorized_test_client.get_receipt(RECEIPT_UUID)

    assert result == payload["entity"]
    assert responses.calls[0].request.url == url


@responses.activate
def test_request_barcode_endpoint(authorized_test_client, api_response):
    """Проверяет POST запроса штрихкода."""
    payload = api_response("barcode_create")
    responses.add(responses.POST, f"{API_URL}v2/print/barcodes", json=payload, status=202)
    orders = [{"order_uuid": ORDER_UUID}]

    result = authorized_test_client.request_barcode(orders, format_type="A6", lang="RUS")

    assert result == payload["entity"]
    assert request_json() == {"orders": orders, "format": "A6", "lang": "RUS"}


@responses.activate
def test_get_barcode_endpoint(authorized_test_client, api_response):
    """Проверяет GET штрихкода."""
    payload = api_response("barcode_get")
    url = f"{API_URL}v2/print/barcodes/{BARCODE_UUID}"
    responses.add(responses.GET, url, json=payload, status=200)

    result = authorized_test_client.get_barcode(BARCODE_UUID)

    assert result == payload["entity"]
    assert responses.calls[0].request.url == url


@responses.activate
def test_download_endpoint(authorized_test_client):
    """Проверяет GET файла печатной формы."""
    url = "https://files.example/waybill.pdf"
    responses.add(responses.GET, url, body=b"%PDF-test", status=200)

    result = authorized_test_client.download(url)

    assert result.getvalue() == b"%PDF-test"
    assert responses.calls[0].request.url == url


@responses.activate
def test_legacy_calculator_endpoint(authorized_test_client, api_response_text):
    """Проверяет GET legacy-калькулятора и реальный XML-ответ 400."""
    payload = api_response_text("legacy_calculator_error")
    url = f"{API_URL}calculator/calculate_price_by_json.php"
    responses.add(responses.GET, url, body=payload, status=400, content_type="application/xml")

    with pytest.raises(HTTPError):
        authorized_test_client.get_shipping_cost({"weight": 1})

    assert request_json() == {"goods": {"weight": 1}, "version": "1.0"}


@responses.activate
def test_calculator_tariff_endpoint(authorized_test_client, api_response):
    """Проверяет POST калькулятора по коду тарифа."""
    payload = api_response("calculator_tariff")
    responses.add(responses.POST, f"{API_URL}v2/calculator/tariff", json=payload, status=200)
    packages = [{"weight": 100, "length": 10, "width": 10, "height": 10}]

    result = authorized_test_client.calculator_tariff(136, {"code": 44}, {"code": 270}, packages)

    assert result == payload
    assert request_json() == {
        "type": 1,
        "tariff_code": 136,
        "from_location": {"code": 44},
        "to_location": {"code": 270},
        "packages": packages,
    }


@responses.activate
def test_create_webhook_endpoint(authorized_test_client, api_response):
    """Проверяет POST вебхука и реальный ответ о лимите публичного аккаунта."""
    payload = api_response("webhook_create_error")
    responses.add(responses.POST, f"{API_URL}v2/webhooks", json=payload, status=400)

    with pytest.raises(HTTPError):
        authorized_test_client.subscribe("https://webhook.invalid/cdek", "ORDER_STATUS")

    assert request_json() == {"url": "https://webhook.invalid/cdek", "type": "ORDER_STATUS"}


@responses.activate
def test_get_webhooks_endpoint(authorized_test_client, api_response):
    """Проверяет GET списка вебхуков."""
    payload = api_response("webhooks")
    responses.add(responses.GET, f"{API_URL}v2/webhooks", json=payload, status=200)

    result = authorized_test_client.subscribe_info()

    assert result == payload
    assert responses.calls[0].request.method == "GET"


@responses.activate
def test_get_webhook_endpoint(authorized_test_client, api_response):
    """Проверяет GET вебхука по UUID."""
    payload = api_response("webhook_get")
    url = f"{API_URL}v2/webhooks/{WEBHOOK_UUID}"
    responses.add(responses.GET, url, json=payload, status=200)

    result = authorized_test_client.subscribe_info_by_uuid(WEBHOOK_UUID)

    assert result == payload
    assert responses.calls[0].request.url == url


@responses.activate
def test_delete_webhook_endpoint(authorized_test_client, api_response):
    """Проверяет DELETE вебхука и реальный ответ для неизвестного UUID."""
    payload = api_response("webhook_delete_error")
    url = f"{API_URL}v2/webhooks/{MISSING_WEBHOOK_UUID}"
    responses.add(responses.DELETE, url, json=payload, status=404)

    result = authorized_test_client.subscribe_delete(MISSING_WEBHOOK_UUID, raise_errors=False)

    assert result == payload
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_get_deliverypoints_endpoint(authorized_test_client, api_response):
    """Проверяет GET списка ПВЗ с текущими именами query-параметров клиента."""
    payload = api_response("deliverypoints")
    responses.add(responses.GET, f"{API_URL}v2/deliverypoints", json=payload, status=200)

    result = authorized_test_client.get_deliverypoints(city_code1=44, tipe="PVZ", have_cash=True)

    assert result == payload
    assert responses.calls[0].request.params == {
        "city_code1": "44",
        "type": "PVZ",
        "have_cash": "True",
    }
