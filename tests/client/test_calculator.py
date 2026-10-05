"""Тесты калькуляторов доставки - API v2 и legacy-калькулятора v1.5."""

from unittest.mock import MagicMock

import pytest
import responses

from gocream_pycdek import CdekClient
from gocream_pycdek import ContractType
from gocream_pycdek.exceptions import CdekNoAuthClientException
from gocream_pycdek.exceptions import CdekRequestException
from gocream_pycdek.utils import get_secure
from tests.helpers import RECORDINGS_PATH
from tests.helpers import FakeResponse
from tests.helpers import json_body
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"


# Контрактные тесты: `send` замокан, сети нет.


def test_calculator_tariff_returns_decoded_response(client):
    """Проверяет декодированный ответ калькулятора API v2."""

    client.send = MagicMock(return_value=FakeResponse({"ok": True}))
    result = client.calculator_tariff(
        10, {"code": 1}, {"code": 2}, [{"weight": 100}], contract_type=ContractType.ONLINE_STORE
    )
    assert result == {"ok": True}


def test_shipping_cost_adds_auth_fields(client, monkeypatch):
    """Проверяет credentials, дату и подпись legacy-калькулятора при `auth=True`."""

    client.send = MagicMock(return_value=FakeResponse({"ok": True}))
    date = MagicMock()
    date.today.return_value.isoformat.return_value = "2024-01-01"
    monkeypatch.setattr("gocream_pycdek.client.dt.date", date)

    with pytest.warns(DeprecationWarning, match="get_shipping_cost"):
        assert client.get_shipping_cost({"weight": 1}, auth=True) == {"ok": True}

    sent_data = client.send.call_args.kwargs["data"]

    assert sent_data["authLogin"] == "client-id"
    assert sent_data["dateExecute"] == "2024-01-01"
    assert "secure" in sent_data


def test_shipping_cost_requires_credentials_when_auth_enabled():
    """Проверяет ошибку legacy-калькулятора при включённой auth без credentials."""

    client = CdekClient("", "")
    with pytest.warns(DeprecationWarning), pytest.raises(CdekNoAuthClientException):
        client.get_shipping_cost({}, auth=True)


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_legacy_calculator_endpoint(authorized_test_client):
    """Проверяет POST legacy-калькулятора с подписью и разбор записанного ответа контура."""

    url = f"{API_URL}calculator/calculate_price_by_json.php"
    resp_json = recorded_response("legacy_calculator")
    responses.add(responses.POST, url, json=resp_json, status=200)

    with pytest.warns(DeprecationWarning):
        result = authorized_test_client.get_shipping_cost(
            {"weight": 1}, sender_city_id=44, receiver_city_id=270, tariff_id=136, date_execute="2026-10-01", auth=True
        )

    sent = only_request(responses.calls)

    assert sent.method == "POST"
    assert json_body(sent) == {
        "version": "1.0",
        "goods": {"weight": 1},
        "senderCityId": 44,
        "receiverCityId": 270,
        "tariffId": 136,
        "dateExecute": "2026-10-01",
        "authLogin": "client-id",
        "secure": get_secure("client-secret", "2026-10-01"),
    }
    assert result == resp_json


@responses.activate
def test_legacy_calculator_without_auth(authorized_test_client):
    """Без `auth=True` контур отвечает XML-ошибкой, и клиент поднимает `CdekRequestException`."""

    url = f"{API_URL}calculator/calculate_price_by_json.php"
    body = (RECORDINGS_PATH / "legacy_calculator_auth_error.xml").read_bytes()
    responses.add(responses.POST, url, body=body, status=400, content_type="application/xml;charset=UTF-8")

    with pytest.warns(DeprecationWarning), pytest.raises(CdekRequestException) as error:
        authorized_test_client.get_shipping_cost({"weight": 1})

    assert b"ERROR_REQUEST_AUTH_IS_EMPTY" in error.value.response.content


@responses.activate
def test_calculator_tariff_endpoint(authorized_test_client):
    """Проверяет тело POST-запроса расчёта по коду тарифа и разбор ответа контура."""

    resp_json = recorded_response("calculator_tariff")
    responses.add(responses.POST, f"{API_URL}v2/calculator/tariff", json=resp_json, status=200)

    request_data = {
        "type": ContractType.ONLINE_STORE,
        "tariff_code": 136,
        "from_location": {"code": 44},
        "to_location": {"code": 270},
        "packages": [{"weight": 100, "length": 10, "width": 10, "height": 10}],
    }

    result = authorized_test_client.calculator_tariff(
        request_data["tariff_code"],
        request_data["from_location"],
        request_data["to_location"],
        request_data["packages"],
        contract_type=request_data["type"],
    )

    sent = only_request(responses.calls)

    assert json_body(sent) == request_data
    assert result == resp_json


def test_calculator_preserves_explicit_values_and_input(client):
    """Калькулятор сохраняет явные и вложенные значения, опуская только верхнеуровневые None."""

    client.send = MagicMock(return_value=FakeResponse({"total_sum": 100}))
    location = {"code": 44, "address": "", "postal_code": None}
    client.calculator_tariff(136, location, {}, [], contract_type=2, date="", currency=0, services=[])

    client.send.assert_called_once_with(
        client.RESOURCE_CALCULATOR_TARIFF,
        method="post",
        data={
            "type": 2,
            "tariff_code": 136,
            "from_location": {"code": 44, "address": "", "postal_code": None},
            "to_location": {},
            "packages": [],
            "date": "",
            "currency": 0,
            "services": [],
        },
    )
    assert location == {"code": 44, "address": "", "postal_code": None}


def test_calculator_returns_raw_response_and_forwards_options(client):
    """Калькулятор возвращает сырой ответ без декодирования и передаёт HTTP-настройки."""

    raw_response = MagicMock()
    client.send = MagicMock(return_value=raw_response)
    result = client.calculator_tariff(
        136,
        {"code": 44},
        {"code": 270},
        [{"weight": 100}],
        contract_type=1,
        origin_response=True,
        raise_errors=False,
        timeout=7,
        headers={},
    )
    assert result is raw_response
    raw_response.json.assert_not_called()
    client.send.assert_called_once_with(
        client.RESOURCE_CALCULATOR_TARIFF,
        method="post",
        data={
            "type": 1,
            "tariff_code": 136,
            "from_location": {"code": 44},
            "to_location": {"code": 270},
            "packages": [{"weight": 100}],
        },
        raise_errors=False,
        timeout=7,
        headers={},
    )


def test_calculator_rejects_unknown_contract_type(client):
    """Неизвестный тип заказа отклоняется до HTTP-запроса."""

    client.send = MagicMock()
    with pytest.raises(ValueError, match="not a valid ContractType"):
        client.calculator_tariff(136, {}, {}, [], contract_type=42)
    client.send.assert_not_called()


@pytest.mark.parametrize("raise_errors", [True, False])
@responses.activate
def test_calculator_http_error(authorized_test_client, raise_errors):
    """HTTP-ошибка расчёта вызывает исключение либо возвращается как JSON при raise_errors=False."""

    error = {"errors": [{"code": "invalid", "message": "Invalid tariff"}]}
    responses.add(responses.POST, f"{API_URL}v2/calculator/tariff", json=error, status=400)
    if raise_errors:
        with pytest.raises(CdekRequestException) as exc_info:
            authorized_test_client.calculator_tariff(136, {}, {}, [], contract_type=1)
        assert exc_info.value.response.json() == error
    else:
        assert authorized_test_client.calculator_tariff(136, {}, {}, [], contract_type=1, raise_errors=False) == error


def test_shipping_cost_warns_at_call_site(client):
    """DeprecationWarning указывает на вызывающий код и сохраняет сырой ответ legacy-метода."""

    raw_response = FakeResponse({"ok": True})
    client.send = MagicMock(return_value=raw_response)
    with pytest.warns(DeprecationWarning, match="removed in 3.0.0; use calculator_tariff") as warnings:
        assert client.get_shipping_cost({}, origin_response=True) is raw_response
    assert warnings[0].filename == __file__
