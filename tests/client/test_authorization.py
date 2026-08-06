"""Тесты авторизации: HTTP-контракт `oauth/token` и разбор ответа."""

import pytest
import responses

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
