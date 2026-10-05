"""Тесты подписок на вебхуки: контракт `send` и endpoint-level HTTP."""

from unittest.mock import MagicMock

import pytest
import responses

from gocream_pycdek.exceptions import CdekRequestException
from tests.helpers import FakeResponse
from tests.helpers import json_body
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"
WEBHOOK_UUID = "55555555-5555-4555-8555-555555555551"
MISSING_WEBHOOK_UUID = "55555555-5555-4555-8555-555555555555"


# Контрактные тесты: `send` замокан, сети нет.


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

    client.send = MagicMock(return_value=FakeResponse({"ok": True}))
    assert getattr(client, method_name)(*args) == {"ok": True}


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_create_webhook_endpoint(authorized_test_client):
    """Проверяет тело POST-запроса подписки и реальный ответ о лимите аккаунта.

    Публичная тестовая учётная запись упёрлась в лимит активных вебхуков, поэтому
    записан ответ с ошибкой: проверяется форма запроса и то, что клиент поднимает
    исключение на 400.
    """

    responses.add(responses.POST, f"{API_URL}v2/webhooks", json=recorded_response("webhook_create_error"), status=400)

    request_data = {"url": "https://webhook.invalid/cdek", "type": "ORDER_STATUS"}

    with pytest.raises(CdekRequestException):
        authorized_test_client.subscribe(request_data["url"], request_data["type"])

    sent = only_request(responses.calls)

    assert json_body(sent) == request_data


@responses.activate
def test_get_webhooks_endpoint(authorized_test_client):
    """Проверяет метод запроса списка вебхуков и разбор ответа контура."""

    resp_json = recorded_response("webhooks")
    responses.add(responses.GET, f"{API_URL}v2/webhooks", json=resp_json, status=200)

    result = authorized_test_client.subscribe_info()

    sent = only_request(responses.calls)

    assert sent.method == "GET"
    assert result == resp_json


@responses.activate
def test_get_webhook_endpoint(authorized_test_client):
    """Проверяет адрес запроса вебхука по UUID и разбор ответа контура."""

    resp_json = recorded_response("webhook_get")
    url = f"{API_URL}v2/webhooks/{WEBHOOK_UUID}"
    responses.add(responses.GET, url, json=resp_json, status=200)

    result = authorized_test_client.subscribe_info_by_uuid(WEBHOOK_UUID)

    sent = only_request(responses.calls)

    assert sent.url == url
    assert result == resp_json


@responses.activate
def test_delete_webhook_endpoint(authorized_test_client):
    """Проверяет метод и адрес удаления вебхука на реальном ответе для чужого UUID."""

    resp_json = recorded_response("webhook_delete_error")
    url = f"{API_URL}v2/webhooks/{MISSING_WEBHOOK_UUID}"
    responses.add(responses.DELETE, url, json=resp_json, status=404)

    result = authorized_test_client.subscribe_delete(MISSING_WEBHOOK_UUID, raise_errors=False)

    sent = only_request(responses.calls)

    assert (sent.method, sent.url) == ("DELETE", url)
    assert result == resp_json


@pytest.mark.parametrize(
    ("method_name", "args", "resource", "http_method", "send_kwargs"),
    [
        (
            "subscribe",
            ("https://webhook.invalid/cdek", "ORDER_STATUS"),
            "v2/webhooks",
            "post",
            {"data": {"url": "https://webhook.invalid/cdek", "type": "ORDER_STATUS"}},
        ),
        ("subscribe_info", (), "v2/webhooks", "get", {}),
        ("subscribe_info_by_uuid", ("u",), "v2/webhooks/u", "get", {}),
        ("subscribe_delete", ("u",), "v2/webhooks/u", "delete", {}),
    ],
)
def test_webhooks_forward_options_and_return_raw_response(
    client, method_name, args, resource, http_method, send_kwargs
):
    """Все операции передают HTTP-настройки и возвращают сырой ответ без декодирования по запросу."""

    raw_response = MagicMock()
    client.send = MagicMock(return_value=raw_response)

    result = getattr(client, method_name)(*args, origin_response=True, raise_errors=False, timeout=7, headers={})

    assert result is raw_response
    raw_response.json.assert_not_called()
    client.send.assert_called_once_with(
        resource, method=http_method, raise_errors=False, timeout=7, headers={}, **send_kwargs
    )


def test_subscribe_preserves_explicit_empty_values(client):
    """Создание подписки сохраняет явно переданные пустые строки для проверки на стороне API."""

    client.send = MagicMock(return_value=FakeResponse({"errors": []}))

    client.subscribe("", "")

    client.send.assert_called_once_with("v2/webhooks", method="post", data={"url": "", "type": ""}, raise_errors=True)


@pytest.mark.parametrize("method_name", ["subscribe", "subscribe_delete"])
@responses.activate
def test_webhook_mutations_preserve_full_json(authorized_test_client, method_name):
    """Успешные создание и удаление возвращают весь JSON, включая служебные requests."""

    payload = {"entity": {"uuid": WEBHOOK_UUID}, "requests": [{"state": "ACCEPTED"}]}
    if method_name == "subscribe":
        method, url, args = responses.POST, f"{API_URL}v2/webhooks", ("https://webhook.invalid/cdek", "ORDER_STATUS")
    else:
        method, url, args = responses.DELETE, f"{API_URL}v2/webhooks/{WEBHOOK_UUID}", (WEBHOOK_UUID,)
    responses.add(method, url, json=payload, status=202)

    assert getattr(authorized_test_client, method_name)(*args) == payload


@pytest.mark.parametrize(
    ("method_name", "args", "resource", "http_method"),
    [
        ("subscribe", ("https://webhook.invalid/cdek", "ORDER_STATUS"), "v2/webhooks", responses.POST),
        ("subscribe_info", (), "v2/webhooks", responses.GET),
        ("subscribe_info_by_uuid", ("u",), "v2/webhooks/u", responses.GET),
        ("subscribe_delete", ("u",), "v2/webhooks/u", responses.DELETE),
    ],
)
@pytest.mark.parametrize("raise_errors", [True, False])
@responses.activate
def test_webhooks_http_errors(authorized_test_client, method_name, args, resource, http_method, raise_errors):
    """HTTP-ошибка вызывает исключение либо возвращается целиком при отключённой проверке."""

    error = {"errors": [{"code": "invalid", "message": "Invalid webhook"}]}
    responses.add(http_method, f"{API_URL}{resource}", json=error, status=400)

    if raise_errors:
        with pytest.raises(CdekRequestException) as exc_info:
            getattr(authorized_test_client, method_name)(*args)
        assert exc_info.value.response.status_code == 400
        assert exc_info.value.response.json() == error
    else:
        assert getattr(authorized_test_client, method_name)(*args, raise_errors=False) == error
