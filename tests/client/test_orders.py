"""Тесты методов работы с заказами: контракт `send` и endpoint-level HTTP."""

from unittest.mock import MagicMock

import pytest
import responses

from gocream_pycdek import ContractType
from tests.helpers import FakeResponse
from tests.helpers import json_body
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"
ORDER_UUID = "11111111-1111-4111-8111-111111111111"


# Контрактные тесты: `send` замокан, сети нет.


def test_registrate_order_extracts_entity(client):
    """Проверяет извлечение `entity` из ответа регистрации заказа."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    result = client.registrate_order(10, {"name": "A"}, [{"weight": 100}], contract_type=ContractType.ONLINE_STORE)
    assert result == {"uuid": "u"}


def test_registrate_order_returns_original_response(client):
    """Проверяет возврат исходного response при `origin_response`."""

    raw_response = FakeResponse({"entity": {"uuid": "u"}})
    client.send = MagicMock(return_value=raw_response)

    result = client.registrate_order(
        10,
        {"name": "A"},
        [{"weight": 100}],
        contract_type=ContractType.ONLINE_STORE,
        origin_response=True,
    )

    assert result is raw_response


def test_registrate_order_builds_payload(client):
    """Проверяет тип заказа магазина и отсутствие непереданных полей в payload."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    client.registrate_order(10, {"name": "A"}, [{"weight": 100}], contract_type=ContractType.ONLINE_STORE)
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


def test_registrate_order_accepts_raw_order_type(client):
    """Проверяет приведение типа заказа, переданного числом вместо `ContractType`."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    client.registrate_order(10, {"name": "A"}, [{"weight": 100}], contract_type=2)

    assert client.send.call_args.kwargs["data"]["type"] == 2


def test_registrate_order_rejects_unknown_order_type(client):
    """Проверяет отказ на типе заказа вне справочника."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))

    with pytest.raises(ValueError, match="not a valid ContractType"):
        client.registrate_order(10, {"name": "A"}, [{"weight": 100}], contract_type=42)

    client.send.assert_not_called()


def test_registrate_order_keeps_passed_empty_values(client):
    """Проверяет, что переданные пустые значения уходят в запрос, а не отбрасываются."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    client.registrate_order(
        10,
        {"name": "A"},
        [{"weight": 100}],
        contract_type=ContractType.ONLINE_STORE,
        comment="",
        services=[],
    )

    payload = client.send.call_args.kwargs["data"]
    assert payload["comment"] == ""
    assert payload["services"] == []


def test_registrate_order_renames_request_print(client):
    """Проверяет отправку `request_print` под именем `print`."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    client.registrate_order(
        10,
        {"name": "A"},
        [{"weight": 100}],
        contract_type=ContractType.ONLINE_STORE,
        request_print="waybill",
    )

    assert client.send.call_args.kwargs["data"]["print"] == "waybill"


def test_registrate_order_forwards_kwargs_to_send(client):
    """Проверяет проброс параметров транспорта в `send`."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    client.registrate_order(
        10,
        {"name": "A"},
        [{"weight": 100}],
        contract_type=ContractType.ONLINE_STORE,
        raise_errors=False,
    )

    assert client.send.call_args.kwargs["raise_errors"] is False


def test_order_lookup_requires_identifier(client):
    """Проверяет ошибку при вызове `get_order` без идентификатора."""

    with pytest.raises(ValueError, match="One of the"):
        client.get_order()


def test_order_lookup_rejects_multiple_identifiers(client):
    """Проверяет ошибку при передаче нескольких идентификаторов заказа."""

    with pytest.raises(ValueError, match="Only one"):
        client.get_order(uuid="u", cdek_number="1")


def test_order_lookup_ignores_empty_identifier(client):
    """Проверяет, что пустой идентификатор считается непереданным."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))

    with pytest.raises(ValueError, match="One of the"):
        client.get_order(uuid="", cdek_number="")

    client.send.assert_not_called()


@pytest.mark.parametrize(
    ("identifier", "value"),
    [
        ("cdek_number", "123"),
        ("im_number", "im-1"),
    ],
    ids=["cdek-number", "im-number"],
)
def test_order_lookup_by_number_sends_query_param(client, identifier, value):
    """Проверяет поиск по номеру: адрес коллекции и query-параметр по имени идентификатора."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))

    assert client.get_order(**{identifier: value}) == {"uuid": "u"}

    client.send.assert_called_once_with("v2/orders", method="get", params={identifier: value})


def test_order_lookup_by_uuid_sends_resource_path(client):
    """Проверяет поиск по uuid: идентификатор уходит адресом ресурса, а не параметром."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))

    assert client.get_order(uuid=ORDER_UUID) == {"uuid": "u"}

    client.send.assert_called_once_with(f"v2/orders/{ORDER_UUID}", method="get", params=None)


def test_order_lookup_returns_original_response(client):
    """Проверяет возврат исходного response при `origin_response`."""

    raw_response = FakeResponse({"entity": {"uuid": "u"}})
    client.send = MagicMock(return_value=raw_response)

    assert client.get_order(uuid=ORDER_UUID, origin_response=True) is raw_response


def test_order_lookup_forwards_kwargs_to_send(client):
    """Проверяет проброс параметров транспорта в `send`."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))
    client.get_order(uuid=ORDER_UUID, origin_response=True, raise_errors=False)

    assert client.send.call_args.kwargs["raise_errors"] is False


def test_remove_order_returns_original_response(client):
    """Проверяет возврат исходного ответа без разбора JSON при `origin_response=True`."""

    raw_response = MagicMock()
    client.send = MagicMock(return_value=raw_response)

    assert client.remove_order("u", origin_response=True) is raw_response
    raw_response.json.assert_not_called()


def test_remove_order_extracts_entity(client):
    """Проверяет извлечение `entity` и строковый адрес DELETE-запроса по умолчанию."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}, "requests": []}))

    assert client.remove_order("u") == {"uuid": "u"}
    client.send.assert_called_once_with("v2/orders/u", method="delete", raise_errors=True)


def test_remove_order_forwards_transport_options(client):
    """Проверяет позиционный `raise_errors` и проброс таймаута в `send`."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"uuid": "u"}}))

    client.remove_order("u", False, timeout=42)

    client.send.assert_called_once_with("v2/orders/u", method="delete", raise_errors=False, timeout=42)


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_register_order_endpoint(authorized_test_client):
    """Проверяет тело POST-запроса регистрации заказа и разбор ответа контура.

    Данные заказа - те же, которыми снимался `order_create.json`, поэтому запрос
    и ответ описывают один и тот же реальный сценарий.
    """

    resp_json = recorded_response("order_create")
    responses.add(responses.POST, f"{API_URL}v2/orders", json=resp_json, status=202)
    request_data = {
        "type": 1,
        "tariff_code": 136,
        "recipient": {"name": "Тестовый получатель", "phones": [{"number": "+70000000001"}]},
        "packages": [{"number": "1", "weight": 100, "length": 10, "width": 10, "height": 10}],
        "number": "fixture-order-1",
        "shipment_point": "MSK65",
        "delivery_point": "NSK23",
    }

    result = authorized_test_client.registrate_order(
        request_data["tariff_code"],
        request_data["recipient"],
        request_data["packages"],
        contract_type=request_data["type"],
        number=request_data["number"],
        shipment_point=request_data["shipment_point"],
        delivery_point=request_data["delivery_point"],
    )

    sent = only_request(responses.calls)
    assert json_body(sent) == request_data
    assert result == resp_json["entity"]


@pytest.mark.parametrize(
    ("identifier", "value"),
    [
        ("cdek_number", "1100000001"),
        ("im_number", "fixture-order-1"),
    ],
    ids=["cdek-number", "im-number"],
)
@responses.activate
def test_get_order_by_number_endpoint(authorized_test_client, identifier, value):
    """Проверяет query-параметр поиска заказа по номеру и разбор ответа контура."""

    resp_json = recorded_response("order_get")
    responses.add(responses.GET, f"{API_URL}v2/orders", json=resp_json, status=200)

    result = authorized_test_client.get_order(**{identifier: value})

    sent = only_request(responses.calls)
    assert sent.params == {identifier: value}
    assert result == resp_json["entity"]


@responses.activate
def test_get_order_by_uuid_endpoint(authorized_test_client):
    """Проверяет адрес поиска заказа по UUID и разбор ответа контура."""

    resp_json = recorded_response("order_get")
    url = f"{API_URL}v2/orders/{ORDER_UUID}"
    responses.add(responses.GET, url, json=resp_json, status=200)

    result = authorized_test_client.get_order(uuid=ORDER_UUID)

    sent = only_request(responses.calls)

    assert sent.url == url
    assert result == resp_json["entity"]


@responses.activate
def test_get_order_returns_error_response_without_raise_errors(authorized_test_client):
    """Проверяет, что `raise_errors=False` доходит до `send` и ошибка возвращается ответом.

    Вместе с ним нужен `origin_response=True`: в теле ошибки нет `entity`, поэтому
    обычный разбор ответа упал бы с `KeyError`.
    """

    url = f"{API_URL}v2/orders/{ORDER_UUID}"
    responses.add(responses.GET, url, json={"errors": [{"code": "not_found"}]}, status=404)

    result = authorized_test_client.get_order(uuid=ORDER_UUID, raise_errors=False, origin_response=True)

    assert result.status_code == 404
    assert result.json() == {"errors": [{"code": "not_found"}]}


@responses.activate
def test_remove_order_endpoint(authorized_test_client):
    """Проверяет метод и адрес удаления заказа, а также извлечение `entity` из ответа контура."""

    resp_json = recorded_response("order_delete")
    url = f"{API_URL}v2/orders/{ORDER_UUID}"
    responses.add(responses.DELETE, url, json=resp_json, status=202)

    result = authorized_test_client.remove_order(ORDER_UUID)

    sent = only_request(responses.calls)

    assert (sent.method, sent.url) == ("DELETE", url)
    assert result == resp_json["entity"]


@responses.activate
def test_remove_order_returns_error_response_without_raise_errors(authorized_test_client):
    """Проверяет возврат ошибки без `entity` при отключённых исключениях и разборе ответа."""

    url = f"{API_URL}v2/orders/{ORDER_UUID}"
    error = {"errors": [{"code": "not_found"}]}
    responses.add(responses.DELETE, url, json=error, status=404)

    result = authorized_test_client.remove_order(ORDER_UUID, raise_errors=False, origin_response=True)

    assert result.status_code == 404
    assert result.json() == error
