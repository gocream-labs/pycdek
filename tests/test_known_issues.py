"""Регрессионные тесты наблюдаемого поведения из списка известных проблем."""

from pathlib import PurePosixPath

import pytest
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

    with pytest.raises(CdekRequestException):
        authorized_client.get_order(uuid="order-uuid", raise_errors=False)


def test_get_url_mangles_absolute_url_passed_as_path(client):
    """Фиксирует порчу абсолютной ссылки, переданной как `PurePath`.

    `as_posix()` схлопывает `//` в схеме до одного слэша, проверка на `https://`
    не срабатывает, и ссылка молча приклеивается к базовому адресу CDEK.
    """

    result = client.get_url(PurePosixPath("https://files.example/waybill.pdf"))

    assert result == "https://api.cdek.ru/https:/files.example/waybill.pdf"
