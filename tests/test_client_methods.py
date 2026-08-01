"""Контрактные тесты публичных методов `CDEKApiClient` без реальной сети."""

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import call

import pytest

from gocream_pycdek.client import CDEKApiClient
from gocream_pycdek.exceptions import CdekNoAuthClientException


class FakeResponse:
    """Минимальная замена `requests.Response` для тестов преобразования ответа."""

    def __init__(self, body=None, content=b"file"):
        self.body = body
        self.content = content

    def json(self):
        return self.body


def response(body, content=b"file"):
    """Создаёт предсказуемый fake response с JSON-телом и содержимым файла."""
    return FakeResponse(body, content)


def test_registrate_order_extracts_entity(client):
    """Проверяет извлечение `entity` из ответа регистрации заказа."""

    client.send = MagicMock(return_value=response({"entity": {"uuid": "u"}}))
    result = client.registrate_order(10, {"name": "A"}, [{"weight": 100}], comment="")
    assert result == {"uuid": "u"}


def test_registrate_order_builds_payload(client):
    """Проверяет тип заказа магазина и удаление пустых полей из payload."""

    client.send = MagicMock(return_value=response({"entity": {"uuid": "u"}}))
    client.registrate_order(10, {"name": "A"}, [{"weight": 100}], comment="")
    client.send.assert_called_once_with(
        "v2/orders",
        method="post",
        data={
            "type": 1,
            "tariff_code": 10,
            "recipient": {"name": "A"},
            "packages": [{"weight": 100}],
        },
    )


def test_order_lookup_requires_identifier(client):
    """Проверяет ошибку при вызове `get_order` без идентификатора."""

    with pytest.raises(Exception, match="Only one"):
        client.get_order()


def test_order_lookup_rejects_multiple_identifiers(client):
    """Проверяет ошибку при передаче нескольких идентификаторов заказа."""

    with pytest.raises(Exception, match="Only one"):
        client.get_order(uuid="u", cdek_number="1")


def test_order_lookup_accepts_single_identifier(client):
    """Проверяет успешный поиск по одному идентификатору и query-параметр."""

    client.send = MagicMock(return_value=response({"entity": {"uuid": "u"}}))
    assert client.get_order(cdek_number="123") == {"uuid": "u"}
    client.send.assert_called_once_with(Path("v2/orders"), params={"cdek_number": "123"})


@pytest.mark.parametrize(
    ("method_name", "resource"),
    [
        ("remove_order", "v2/orders/u"),
        ("remove_intakes", "v2/intakes/u"),
    ],
)
def test_delete_methods_return_original_response(client, method_name, resource):
    """Проверяет текущий контракт delete-методов: возвращается исходный response."""

    raw_response = response({"entity": {"uuid": "u"}})
    client.send = MagicMock(return_value=raw_response)

    assert getattr(client, method_name)("u", raise_errors=False) is raw_response
    client.send.assert_called_once_with(Path(resource), method="delete", raise_errors=False)


@pytest.mark.parametrize(
    ("method_name", "args"),
    [
        ("get_intakes", ("u",)),
        ("get_receipt", ("u",)),
        ("get_barcode", ("u",)),
        ("download", ("https://files.example/doc",)),
    ],
    ids=["get-intakes", "get-receipt", "get-barcode", "download"],
)
def test_origin_response_preserves_original_response(client, method_name, args):
    """Проверяет единый контракт `origin_response=True` у поддерживающих его методов."""

    raw_response = response({"entity": {"uuid": "u"}})
    client.send = MagicMock(return_value=raw_response)
    assert getattr(client, method_name)(*args, origin_response=True) is raw_response


def test_registrate_intakes_extracts_entity(client):
    """Проверяет регистрацию забора и извлечение `entity` из ответа."""

    client.send = MagicMock(return_value=response({"entity": {"id": 1}}))
    assert client.registrate_intakes("2024-01-01", "10:00", "18:00") == {"id": 1}


def test_get_intakes_extracts_entity(client):
    """Проверяет извлечение `entity` при получении информации о заборе."""

    client.send = MagicMock(return_value=response({"entity": {"id": 1}}))
    assert client.get_intakes("u") == {"id": 1}


@pytest.mark.parametrize("method_name", ["request_receipt", "request_barcode"])
def test_request_document_extracts_entity(client, method_name):
    """Проверяет извлечение `entity` при запросе квитанции и штрихкода."""

    client.send = MagicMock(return_value=response({"entity": {"id": 1}}))
    assert getattr(client, method_name)([{"order_uuid": "u"}]) == {"id": 1}


@pytest.mark.parametrize("method_name", ["get_receipt", "get_barcode"])
def test_get_document_extracts_entity(client, method_name):
    """Проверяет извлечение `entity` при получении квитанции и штрихкода."""

    client.send = MagicMock(return_value=response({"entity": {"id": 1}}))
    assert getattr(client, method_name)("u") == {"id": 1}


def test_get_regions_returns_decoded_response(client):
    """Проверяет параметры и декодированный ответ справочника регионов."""

    client.send = MagicMock(return_value=response([{"code": 1}]))
    assert client.get_regions(country_codes=["RU"], page=0) == [{"code": 1}]
    client.send.assert_called_once_with(
        Path("v2/location/regions"),
        params={"country_codes": ["RU"], "size": 1000, "page": 0},
        raise_errors=True,
    )


def test_get_cities_returns_decoded_response(client):
    """Проверяет параметры и декодированный ответ справочника городов."""

    client.send = MagicMock(return_value=response([{"code": 1}]))
    assert client.get_cities(city="Moscow") == [{"code": 1}]
    client.send.assert_called_once_with(
        Path("v2/location/cities"),
        params={"city": "Moscow", "page": 0, "size": 1000},
        raise_errors=True,
    )


@pytest.mark.parametrize(
    ("all_method_name", "page_method_name"),
    [
        ("get_all_regions", "get_regions"),
        ("get_all_cities", "get_cities"),
    ],
    ids=["regions", "cities"],
)
def test_pagination_generators_reset_page_and_stop_on_empty(client, all_method_name, page_method_name):
    """Проверяет сброс страницы, последовательный обход страниц и остановку на пустом ответе."""

    page_method = MagicMock(side_effect=[[{"code": 1}], [{"code": 2}], []])
    setattr(client, page_method_name, page_method)

    assert list(getattr(client, all_method_name)(page=99)) == [{"code": 1}, {"code": 2}]
    assert page_method.call_args_list == [
        call(page=0, origin_response=False),
        call(page=1, origin_response=False),
        call(page=2, origin_response=False),
    ]


def test_download_returns_bytes_io(client):
    """Проверяет преобразование содержимого скачанного файла в `BytesIO`."""

    client.send = MagicMock(return_value=response({"ok": True}, b"PDF"))
    result = client.download("https://files.example/doc")
    assert isinstance(result, BytesIO)
    assert result.getvalue() == b"PDF"


def test_calculator_tariff_returns_decoded_response(client):
    """Проверяет декодированный ответ калькулятора API v2."""

    client.send = MagicMock(return_value=response({"ok": True}))
    assert client.calculator_tariff(10, {"code": 1}, {"code": 2}, [{"weight": 100}]) == {"ok": True}


def test_shipping_cost_adds_auth_fields(client, monkeypatch):
    """Проверяет credentials, дату и подпись legacy-калькулятора при `auth=True`."""

    client.send = MagicMock(return_value=response({"ok": True}))
    date = MagicMock()
    date.today.return_value.isoformat.return_value = "2024-01-01"
    monkeypatch.setattr("gocream_pycdek.client.dt.date", date)

    assert client.get_shipping_cost({"weight": 1}, auth=True) == {"ok": True}

    sent = client.send.call_args.kwargs["data"]
    assert sent["authLogin"] == "client-id"
    assert sent["dateExecute"] == "2024-01-01"
    assert "secure" in sent


def test_shipping_cost_requires_credentials_when_auth_enabled():
    """Проверяет ошибку legacy-калькулятора при включённой auth без credentials."""

    client = CDEKApiClient(None, None, is_shop=True)
    with pytest.raises(CdekNoAuthClientException):
        client.get_shipping_cost({}, auth=True)


@pytest.mark.parametrize(
    ("method_name", "args"),
    [
        ("subscribe", ("https://hook.example", "ORDER_STATUS")),
        ("subscribe_info", ()),
        ("subscribe_info_by_uuid", ("u",)),
        ("subscribe_delete", ("u",)),
    ],
    ids=["create", "list", "get", "delete"],
)
def test_webhook_methods_return_decoded_response(client, method_name, args):
    """Проверяет декодирование ответов всех реализованных операций с вебхуками."""

    client.send = MagicMock(return_value=response({"ok": True}))
    assert getattr(client, method_name)(*args) == {"ok": True}


def test_deliverypoints_maps_tipe_to_type_parameter(client):
    """Проверяет преобразование аргумента `tipe` в API-параметр `type`."""

    client.send = MagicMock(return_value=response({"ok": True}))
    assert client.get_deliverypoints(city_code1=1, tipe="PVZ") == {"ok": True}
    client.send.assert_called_once_with(
        Path("v2/deliverypoints"),
        params={"city_code1": 1, "type": "PVZ"},
        raise_errors=True,
    )
