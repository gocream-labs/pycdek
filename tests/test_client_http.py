"""Проверки HTTP-слоя: авторизация, URL, заголовки и кэш токена."""

import json
from datetime import datetime
from datetime import timedelta
from pathlib import PureWindowsPath

import pytest
import responses

from gocream_pycdek import PRODUCTION_API_URL
from gocream_pycdek import TEST_API_URL
from gocream_pycdek import CdekClient
from gocream_pycdek import ContractType
from gocream_pycdek.exceptions import CdekApiAccessException
from gocream_pycdek.exceptions import CdekApiUnavailableException
from gocream_pycdek.exceptions import CdekApiWrongTokenTypeException


@responses.activate
def test_authorization_returns_token_response(client):
    """Проверяет возврат декодированного успешного ответа авторизации."""

    responses.add(
        responses.POST,
        "https://api.cdek.ru/v2/oauth/token",
        json={
            "access_token": "fixture.jwt.token",
            "expires_in": 3599,
            "jti": "00000000-0000-4000-8000-000000000000",
            "scope": "location:all order:all payment:all",
            "token_type": "bearer",
        },
        status=200,
    )

    assert client.authorization() == {
        "access_token": "fixture.jwt.token",
        "expires_in": 3599,
        "jti": "00000000-0000-4000-8000-000000000000",
        "scope": "location:all order:all payment:all",
        "token_type": "bearer",
    }


@responses.activate
def test_authorization_sends_credentials_in_query_params(client):
    """Фиксирует текущую передачу credentials в query string POST-запроса."""

    responses.add(
        responses.POST,
        "https://api.cdek.ru/v2/oauth/token",
        json={"token_type": "bearer"},
        status=200,
    )
    client.authorization()

    request = responses.calls[0].request
    assert request.method == "POST"
    assert request.params == {
        "grant_type": "client_credentials",
        "client_id": "client-id",
        "client_secret": "client-secret",
    }


@pytest.mark.xfail(
    reason="Клиент не читает значение поля error из ответа invalid_client",
    strict=True,
)
@responses.activate
def test_authorization_maps_invalid_client(client, api_response):
    """Проверяет реальный ответ `invalid_client` тестового контура."""

    payload = api_response("auth_invalid_client")
    responses.add(responses.POST, "https://api.cdek.ru/v2/oauth/token", json=payload, status=401)

    with pytest.raises(CdekApiAccessException):
        client.authorization()


@responses.activate
def test_authorization_maps_service_unavailable(client):
    """Проверяет преобразование ответа о недоступности API."""

    responses.add(
        responses.POST,
        "https://api.cdek.ru/v2/oauth/token",
        json={"reason": "Service Unavailable"},
        status=503,
    )

    with pytest.raises(CdekApiUnavailableException):
        client.authorization()


@responses.activate
def test_authorization_rejects_non_bearer_token(client):
    """Проверяет отказ от неподдерживаемого типа JWT-токена."""

    responses.add(
        responses.POST,
        "https://api.cdek.ru/v2/oauth/token",
        json={"access_token": "token", "token_type": "Basic"},
        status=200,
    )

    with pytest.raises(CdekApiWrongTokenTypeException):
        client.authorization()


@pytest.mark.parametrize(
    ("base_url", "expected_url"),
    [
        (PRODUCTION_API_URL, "https://api.cdek.ru/v2/orders"),
        (TEST_API_URL, "https://api.edu.cdek.ru/v2/orders"),
        ("https://cdek.example.test/api/", "https://cdek.example.test/api/v2/orders"),
    ],
)
def test_get_url_uses_base_url(base_url, expected_url):
    """Проверяет сборку относительного URL для разных API endpoints."""

    client = CdekClient(
        "client-id",
        "client-secret",
        contract_type=ContractType.ONLINE_STORE,
        base_url=base_url,
    )

    assert client.get_url("v2/orders") == expected_url


def test_get_url_preserves_absolute_url():
    """Проверяет, что абсолютная ссылка не дополняется адресом CDEK API."""

    client = CdekClient(
        "client-id",
        "client-secret",
        contract_type=ContractType.ONLINE_STORE,
        base_url="https://unused.example.test",
    )

    assert client.get_url("https://example.test/path") == "https://example.test/path"


def test_get_url_normalizes_path_separator():
    """Проверяет преобразование системного пути в URL-путь."""

    client = CdekClient(
        "client-id",
        "client-secret",
        contract_type=ContractType.ONLINE_STORE,
        base_url="https://cdek.example.test/api",
    )

    assert client.get_url(PureWindowsPath("v2/orders")) == "https://cdek.example.test/api/v2/orders"







def test_get_headers_uses_cached_bearer_token(client):
    """Проверяет формат Authorization-заголовка с действующим токеном."""

    client._token = "token"
    client._token_expires_at = datetime.now() + timedelta(hours=1)
    assert client.get_headers() == {"Authorization": "Bearer token"}


@pytest.mark.parametrize("method", ["get", "post", "delete"])
@responses.activate
def test_send_dispatches_supported_http_methods(client, method):
    """Проверяет отправку каждого поддерживаемого HTTP-метода."""
    client._token = "token"
    client._token_expires_at = datetime.now() + timedelta(hours=1)
    responses.add(method.upper(), "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    assert client.send("v2/orders", method=method).json() == {"ok": True}


@responses.activate
def test_send_passes_common_request_options(client):
    """Проверяет JSON, query-параметры, Bearer-заголовок и timeout запроса."""
    client._token = "token"
    client._token_expires_at = datetime.now() + timedelta(hours=1)
    responses.add(responses.POST, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    client.send("v2/orders", method="post", data={"x": 1}, params={"page": 2})

    request = responses.calls[0].request
    assert request.body == json.dumps({"x": 1}).encode()
    assert request.params == {"page": "2"}
    assert responses.calls[0].request.headers["Authorization"] == "Bearer token"
    assert request.req_kwargs["timeout"] == (3, 7)


def test_token_is_cached_until_expiration(client, monkeypatch):
    """Проверяет, что повторное обращение до истечения срока не вызывает auth API снова."""

    calls = []
    monkeypatch.setattr(
        client, "authorization", lambda: calls.append(1) or {"access_token": "token", "token_type": "bearer"}
    )
    monkeypatch.setattr("gocream_pycdek.client.jwt.decode", lambda *args, **kwargs: {"exp": 4102444800})

    assert client.token == "token"
    assert client.token == "token"
    assert calls == [1]
