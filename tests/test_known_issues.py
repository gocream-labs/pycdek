"""Регрессионные тесты наблюдаемого поведения из списка известных проблем."""

from pathlib import PureWindowsPath

import pytest
from requests import HTTPError
import responses

from gocream_pycdek.exceptions import CdekRequestException


@responses.activate
def test_get_order_does_not_forward_raise_errors(authorized_client):
    """Фиксирует игнорирование `raise_errors=False` методом получения заказа."""
    responses.add(
        responses.GET,
        "https://api.cdek.ru/v2/orders/order-uuid",
        json={"errors": [{"code": "not_found"}]},
        status=404,
    )

    with pytest.raises(HTTPError):
        authorized_client.get_order(uuid="order-uuid", raise_errors=False)


def test_get_url_uses_platform_path_separator(client, monkeypatch):
    """Фиксирует обратные слеши в URL при использовании WindowsPath."""
    monkeypatch.setattr("gocream_pycdek.client.Path", PureWindowsPath)

    assert client.get_url("v2/orders") == "https://api.cdek.ru\\v2\\orders"


def test_send_with_unsupported_method_raises_unbound_local_error(authorized_client):
    """Фиксирует текущую ошибку `send()` для неподдерживаемого HTTP-метода."""
    with pytest.raises(UnboundLocalError):
        authorized_client.send("v2/orders", method="patch")


@responses.activate
def test_send_exposes_requests_http_error_instead_of_wrapper(authorized_client):
    """Фиксирует, что объявленный `CdekRequestException` не используется."""
    responses.add(
        responses.GET,
        "https://api.cdek.ru/v2/orders",
        json={"errors": [{"code": "service_unavailable"}]},
        status=503,
    )

    with pytest.raises(HTTPError) as error:
        authorized_client.send("v2/orders")

    assert not isinstance(error.value, CdekRequestException)
