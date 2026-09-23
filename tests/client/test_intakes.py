"""Тесты методов заявок на забор: контракт `send` и endpoint-level HTTP."""

from unittest.mock import MagicMock

import pytest
import responses

from gocream_pycdek.exceptions import CdekRequestException
from tests.helpers import FakeResponse
from tests.helpers import json_body
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"
INTAKE_UUID = "22222222-2222-4222-8222-222222222222"


# Контрактные тесты: `send` замокан, сети нет.


def test_registrate_intakes_extracts_entity(client):
    """Проверяет регистрацию забора и извлечение `entity` из ответа."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"id": 1}}))
    assert client.registrate_intakes("2024-01-01", "10:00", "18:00") == {"id": 1}


def test_get_intakes_extracts_entity(client):
    """Проверяет извлечение `entity` при получении информации о заборе."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"id": 1}}))
    assert client.get_intakes("u") == {"id": 1}


def test_get_intakes_preserves_original_response(client):
    """Проверяет контракт `origin_response=True` при получении информации о заборе."""

    raw_response = FakeResponse({"entity": {"id": 1}})
    client.send = MagicMock(return_value=raw_response)
    assert client.get_intakes("u", origin_response=True) is raw_response


def test_remove_intakes_returns_original_response(client):
    """Проверяет текущий контракт удаления забора: возвращается исходный response."""

    raw_response = FakeResponse({"entity": {"id": 1}})
    client.send = MagicMock(return_value=raw_response)

    assert client.remove_intakes("u", raise_errors=False) is raw_response
    client.send.assert_called_once_with("v2/intakes/u", method="delete", raise_errors=False)


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_register_intake_endpoint(authorized_test_client):
    """Проверяет тело POST-запроса заявки на забор и разбор ответа контура."""

    resp_json = recorded_response("intake_create")
    responses.add(responses.POST, f"{API_URL}v2/intakes", json=resp_json, status=202)

    request_data = {
        "intake_date": "2026-08-03",
        "intake_time_from": "10:00",
        "intake_time_to": "18:00",
        "name": "Тестовая посылка",
        "weight": 100,
        "length": 10,
        "width": 10,
        "height": 10,
        "sender": {"name": "Тестовый отправитель", "phones": [{"number": "+70000000000"}]},
        "from_location": {"code": 44, "country_code": "RU", "address": "Тестовый адрес отправителя"},
    }

    result = authorized_test_client.registrate_intakes(
        request_data["intake_date"],
        request_data["intake_time_from"],
        request_data["intake_time_to"],
        name=request_data["name"],
        weight=request_data["weight"],
        length=request_data["length"],
        width=request_data["width"],
        height=request_data["height"],
        sender=request_data["sender"],
        from_location=request_data["from_location"],
    )

    sent = only_request(responses.calls)

    assert json_body(sent) == request_data
    assert result == resp_json["entity"]


@responses.activate
def test_get_intake_endpoint(authorized_test_client):
    """Проверяет адрес запроса заявки на забор и разбор ответа контура."""

    resp_json = recorded_response("intake_get")
    url = f"{API_URL}v2/intakes/{INTAKE_UUID}"
    responses.add(responses.GET, url, json=resp_json, status=200)

    result = authorized_test_client.get_intakes(INTAKE_UUID)

    sent = only_request(responses.calls)

    assert sent.url == url
    assert result == resp_json["entity"]


@responses.activate
def test_remove_intake_endpoint(authorized_test_client):
    """Проверяет метод и адрес удаления заявки на забор, а также сырой ответ контура."""

    resp_json = recorded_response("intake_delete")
    url = f"{API_URL}v2/intakes/{INTAKE_UUID}"
    responses.add(responses.DELETE, url, json=resp_json, status=202)

    result = authorized_test_client.remove_intakes(INTAKE_UUID)

    sent = only_request(responses.calls)

    assert (sent.method, sent.url) == ("DELETE", url)
    assert result.json() == resp_json


@pytest.mark.parametrize(
    ("method_name", "args", "http_method", "resource", "send_kwargs"),
    [
        (
            "registrate_intakes",
            ("2026-08-03", "10:00", "18:00"),
            "post",
            "v2/intakes",
            {"data": {"intake_date": "2026-08-03", "intake_time_from": "10:00", "intake_time_to": "18:00"}},
        ),
        ("get_intakes", ("u",), "get", "v2/intakes/u", {}),
        ("remove_intakes", ("u",), "delete", "v2/intakes/u", {}),
    ],
)
def test_intake_methods_forward_request_options(client, method_name, args, http_method, resource, send_kwargs):
    """Все три метода передают HTTP-настройки и флаг ошибок в `send`."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"id": 1}}))

    getattr(client, method_name)(*args, raise_errors=False, timeout=7, headers={"X-Test": "intake"})

    client.send.assert_called_once_with(
        resource, method=http_method, raise_errors=False, timeout=7, headers={"X-Test": "intake"}, **send_kwargs
    )


@responses.activate
def test_register_intake_preserves_explicit_values(authorized_test_client):
    """Регистрация опускает только верхнеуровневые None, сохраняя явные и вложенные значения."""

    responses.add(responses.POST, f"{API_URL}v2/intakes", json={"entity": {"id": 1}}, status=202)
    sender = {"name": "", "company": None, "phones": []}

    authorized_test_client.registrate_intakes(
        "2026-08-03", "10:00", "18:00", comment="", sender=sender, from_location={}, need_call=False, weight=0
    )

    assert json_body(only_request(responses.calls)) == {
        "intake_date": "2026-08-03",
        "intake_time_from": "10:00",
        "intake_time_to": "18:00",
        "comment": "",
        "sender": {"name": "", "company": None, "phones": []},
        "from_location": {},
        "need_call": False,
        "weight": 0,
    }
    assert sender == {"name": "", "company": None, "phones": []}


@pytest.mark.parametrize(
    ("method_name", "args", "http_method", "resource"),
    [
        ("registrate_intakes", ("2026-08-03", "10:00", "18:00"), responses.POST, "v2/intakes"),
        ("get_intakes", (INTAKE_UUID,), responses.GET, f"v2/intakes/{INTAKE_UUID}"),
        ("remove_intakes", (INTAKE_UUID,), responses.DELETE, f"v2/intakes/{INTAKE_UUID}"),
    ],
)
@pytest.mark.parametrize("raise_errors", [True, False])
@responses.activate
def test_intake_http_errors(authorized_test_client, method_name, args, http_method, resource, raise_errors):
    """HTTP-ошибка вызывает исключение либо доступна в сыром ответе при отключённой проверке."""

    error = {"requests": [{"errors": [{"code": "invalid", "message": "Invalid intake"}]}]}
    responses.add(http_method, f"{API_URL}{resource}", json=error, status=400)
    kwargs = {"raise_errors": raise_errors}
    if method_name != "remove_intakes":
        kwargs["origin_response"] = True

    if raise_errors:
        with pytest.raises(CdekRequestException) as exc_info:
            getattr(authorized_test_client, method_name)(*args, **kwargs)
        assert exc_info.value.response.status_code == 400
        assert exc_info.value.response.json() == error
    else:
        result = getattr(authorized_test_client, method_name)(*args, **kwargs)
        assert result.status_code == 400
        assert result.json() == error
