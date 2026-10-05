"""Проверки транспортного слоя клиента: URL, заголовки, кэш токена и отправка запроса."""

import json
from datetime import datetime
from datetime import timedelta
from pathlib import PurePosixPath
from pathlib import PureWindowsPath
from unittest.mock import MagicMock

import jwt
import pytest
import responses
from requests import HTTPError
from requests import RequestException

from gocream_pycdek import PRODUCTION_API_URL
from gocream_pycdek import TEST_API_URL
from gocream_pycdek import CdekClient
from gocream_pycdek.exceptions import CdekRequestException
from tests.helpers import only_request


def stub_authorization(client, expires_at):
    """Подменяет `authorization` ответом с JWT, истекающим в `expires_at`, и возвращает этот токен.

    HTTP-контракт самой авторизации проверяет `test_authorization.py`, поэтому тестам кэша
    токена и заголовков сеть не нужна. А вот JWT настоящий: срок жизни клиент достаёт из
    payload сам, и подмена строкой сломала бы `jwt.decode`. Подпись клиент не проверяет.
    """

    access_token = jwt.encode({"exp": int(expires_at.timestamp())}, "signature-is-not-verified-by-client")
    client.authorization = MagicMock(return_value={"access_token": access_token, "token_type": "bearer"})

    return access_token


def test_token_requests_token_on_first_access(client):
    """Проверяет запрос токена при первом обращении и разбор срока жизни из JWT."""

    # Секунды без микросекунд: `exp` целочисленный, иначе точного сравнения не выйдет.
    expires_at = datetime.now().replace(microsecond=0) + timedelta(hours=1)
    expected_token = stub_authorization(client, expires_at)

    assert client.token == expected_token
    assert client._token_expires_at == expires_at
    client.authorization.assert_called_once_with()


def test_token_is_cached_until_expiration(client):
    """Проверяет, что повторное обращение до истечения срока не вызывает `authorization` снова."""

    expected_token = stub_authorization(client, datetime.now() + timedelta(hours=1))

    assert client.token == expected_token
    assert client.token == expected_token
    client.authorization.assert_called_once_with()


def test_token_is_refreshed_after_expiration(client):
    """Проверяет повторную авторизацию, когда срок действия кэшированного токена истёк."""

    client._token = "expired-token"
    client._token_expires_at = datetime.now() - timedelta(seconds=1)
    expected_token = stub_authorization(client, datetime.now() + timedelta(hours=1))

    assert client.token == expected_token
    client.authorization.assert_called_once_with()


def test_token_is_refreshed_inside_safety_window(client):
    """Проверяет обновление токена, который истекает внутри `TOKEN_REFRESH_MARGIN`."""

    # Нулевой запас превратил бы тест в проверку истёкшего токена, а смысл теста в том,
    # что клиент идёт за новым заранее. Половина запаса - это ещё действующий токен.
    assert timedelta(0) < CdekClient.TOKEN_REFRESH_MARGIN

    client._token = "almost-expired-token"
    client._token_expires_at = datetime.now() + CdekClient.TOKEN_REFRESH_MARGIN / 2
    expected_token = stub_authorization(client, datetime.now() + timedelta(hours=1))

    assert client.token == expected_token
    client.authorization.assert_called_once_with()


def test_token_is_reused_outside_safety_window(client):
    """Проверяет, что токен, живущий дольше `TOKEN_REFRESH_MARGIN`, используется без авторизации."""

    client._token = "cached-token"
    client._token_expires_at = datetime.now() + CdekClient.TOKEN_REFRESH_MARGIN * 2
    # Просто подстарховка что бы в случае чего не было реального вызова
    stub_authorization(client, datetime.now() + timedelta(hours=1))

    assert client.token == "cached-token"
    client.authorization.assert_not_called()


def test_token_is_requested_when_expiration_is_unknown(client):
    """Проверяет авторизацию, когда срок действия токена не сохранён."""

    client._token = "token-without-expiration"
    client._token_expires_at = None
    expected_token = stub_authorization(client, datetime.now() + timedelta(hours=1))

    assert client.token == expected_token
    client.authorization.assert_called_once_with()


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

    client = CdekClient("client-id", "client-secret", base_url=base_url)

    assert client.get_url("v2/orders") == expected_url


@pytest.mark.parametrize(
    "url",
    ["https://example.test/path", "http://example.test/path"],
    ids=["https", "http"],
)
def test_get_url_preserves_absolute_url(url):
    """Проверяет, что абсолютная ссылка не дополняется адресом CDEK API."""

    client = CdekClient("client-id", "client-secret", base_url="https://unused.example.test")

    assert client.get_url(url) == url


@pytest.mark.parametrize(
    "resource",
    ["v2/orders", "/v2/orders", PurePosixPath("v2/orders"), PureWindowsPath("v2\\orders")],
    ids=["relative", "leading-slash", "posix-path", "windows-path"],
)
def test_get_url_normalizes_resource(resource):
    """Проверяет, что путь ресурса приводится к URL-виду независимо от формы записи."""

    client = CdekClient("client-id", "client-secret", base_url="https://cdek.example.test/api")

    assert client.get_url(resource) == "https://cdek.example.test/api/v2/orders"


def test_get_headers_uses_cached_bearer_token(client):
    """Проверяет формат Authorization-заголовка с действующим токеном."""

    client._token = "token"
    client._token_expires_at = datetime.now() + timedelta(hours=1)
    assert client.get_headers() == {"Authorization": "Bearer token"}


def test_get_headers_authorizes_when_token_is_missing(client):
    """Проверяет, что заголовки берут токен через `token`, а не только из кэша."""

    expected_token = stub_authorization(client, datetime.now() + timedelta(hours=1))

    assert client.get_headers() == {"Authorization": f"Bearer {expected_token}"}
    client.authorization.assert_called_once_with()


@pytest.mark.parametrize("method", ["get", "post", "delete", "put", "patch"])
@responses.activate
def test_send_dispatches_any_http_method(authorized_client, method):
    """Проверяет отправку произвольного HTTP-метода, а не только трёх зашитых."""

    responses.add(method.upper(), "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    assert authorized_client.send("v2/orders", method=method).json() == {"ok": True}

    sent = only_request(responses.calls)

    assert sent.method == method.upper()


def test_send_requires_explicit_method(authorized_client):
    """Проверяет, что HTTP-метод обязателен и не подставляется по умолчанию."""

    with pytest.raises(TypeError):
        authorized_client.send("v2/orders")


@responses.activate
def test_send_passes_common_request_options(authorized_client):
    """Проверяет JSON, query-параметры, Bearer-заголовок и timeout запроса."""

    responses.add(responses.POST, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    authorized_client.send("v2/orders", method="post", data={"x": 1}, params={"page": 2})

    sent = only_request(responses.calls)

    assert sent.body == json.dumps({"x": 1}).encode()
    assert sent.params == {"page": "2"}
    assert sent.headers["Authorization"] == "Bearer token"
    assert sent.req_kwargs["timeout"] == (3, 7)


@responses.activate
def test_send_replaces_headers_entirely(authorized_client):
    """Проверяет, что свой набор заголовков вытесняет умолчания, включая `Authorization`."""

    responses.add(responses.GET, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    authorized_client.send("v2/orders", method="get", headers={"Authorization": "Basic custom"})

    sent = only_request(responses.calls)

    assert sent.headers["Authorization"] == "Basic custom"


@responses.activate
def test_send_makes_anonymous_request_without_authorizing(client):
    """Проверяет анонимный запрос: пустые заголовки и ни одного похода за токеном.

    Токен здесь не подставлен намеренно: `authorization` замокан и покажет обращение,
    если клиент всё-таки полезет за ним. Раньше полез бы - `get_headers()` вычислялся
    как аргумент `setdefault` независимо от переданных заголовков.
    """

    stub_authorization(client, datetime.now() + timedelta(hours=1))
    responses.add(responses.GET, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    client.send("v2/orders", method="get", headers={})

    sent = only_request(responses.calls)

    assert "Authorization" not in sent.headers
    client.authorization.assert_not_called()


@responses.activate
def test_send_allows_overriding_timeout(authorized_client):
    """Проверяет, что переданный timeout вытесняет `DEFAULT_TIMEOUT`."""

    responses.add(responses.GET, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    authorized_client.send("v2/orders", method="get", timeout=42)

    sent = only_request(responses.calls)

    assert sent.req_kwargs["timeout"] == 42


@responses.activate
def test_send_wraps_error_status_in_cdek_exception(authorized_client):
    """Проверяет обёртку ошибочного статуса в `CdekRequestException` с исходным ответом."""

    responses.add(
        responses.GET,
        "https://api.cdek.ru/v2/orders",
        json={"errors": [{"code": "service_unavailable"}]},
        status=503,
    )

    with pytest.raises(CdekRequestException) as error:
        authorized_client.send("v2/orders", method="get")

    assert isinstance(error.value, RequestException)
    assert error.value.response.status_code == 503
    assert error.value.response.json() == {"errors": [{"code": "service_unavailable"}]}
    assert isinstance(error.value.__cause__, HTTPError)


@responses.activate
def test_send_returns_error_response_when_errors_are_not_raised(authorized_client):
    """Проверяет возврат ответа с ошибочным статусом при `raise_errors=False`."""

    responses.add(responses.GET, "https://api.cdek.ru/v2/orders", json={"reason": "nope"}, status=404)

    response = authorized_client.send("v2/orders", method="get", raise_errors=False)

    assert response.status_code == 404
    assert response.json() == {"reason": "nope"}


@responses.activate
def test_send_goes_through_client_session(authorized_client):
    """Проверяет отправку через сессию клиента: её настройки видны в запросе."""

    authorized_client._session.headers["X-Session-Marker"] = "shared"
    responses.add(responses.GET, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    authorized_client.send("v2/orders", method="get")

    sent = only_request(responses.calls)

    assert sent.headers["X-Session-Marker"] == "shared"


def test_close_releases_session(client):
    """Проверяет освобождение соединений сессии по `close`."""

    session = client._session = MagicMock()
    client.close()

    session.close.assert_called_once_with()


@responses.activate
def test_client_stays_usable_after_close(authorized_client):
    """Проверяет, что закрытый клиент открывает соединение заново, а не ломается."""

    responses.add(responses.GET, "https://api.cdek.ru/v2/orders", json={"ok": True}, status=200)

    authorized_client.send("v2/orders", method="get")
    authorized_client.close()

    assert authorized_client.send("v2/orders", method="get").json() == {"ok": True}


def test_close_is_idempotent(authorized_client):
    """Проверяет, что повторное закрытие не выбрасывает ошибку."""

    authorized_client.close()
    authorized_client.close()


def test_client_closes_session_on_context_exit(client):
    """Проверяет закрытие сессии при выходе из контекстного менеджера."""

    session = client._session = MagicMock()

    with client as entered:
        assert entered is client

    session.close.assert_called_once_with()
