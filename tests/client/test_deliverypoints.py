"""Тесты списка пунктов выдачи заказов."""

from unittest.mock import MagicMock

import pytest
import responses

from gocream_pycdek.exceptions import CdekRequestException
from tests.helpers import FakeResponse
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"


# Контрактные тесты: `send` замокан, сети нет.


def test_deliverypoints_passes_city_and_type_filters(client):
    """Проверяет передачу фильтров города и типа офиса в query-параметры."""

    client.send = MagicMock(return_value=FakeResponse([{"code": "PVZ1"}]))
    assert client.get_deliverypoints(city_code=1, type="PVZ") == [{"code": "PVZ1"}]
    client.send.assert_called_once_with(
        "v2/deliverypoints",
        method="get",
        params={"city_code": 1, "type": "PVZ"},
        raise_errors=True,
    )


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_get_deliverypoints_endpoint(authorized_test_client):
    """Проверяет query-параметры списка ПВЗ и разбор ответа контура.

    Имена аргументов Python совпадают с query-параметрами API.
    """

    resp_json = recorded_response("deliverypoints")
    responses.add(responses.GET, f"{API_URL}v2/deliverypoints", json=resp_json, status=200)

    request_params = {"postal_code": "010000", "city_code": 44, "type": "PVZ", "have_cash": True}

    result = authorized_test_client.get_deliverypoints(**request_params)

    sent = only_request(responses.calls)

    assert sent.params == {"postal_code": "010000", "city_code": "44", "type": "PVZ", "have_cash": "True"}
    assert result == resp_json


@pytest.mark.parametrize("filters", [{}, {"country_code": "", "have_cash": False, "weight_max": 0}])
def test_deliverypoints_preserves_explicit_filters(client, filters):
    """Непереданные фильтры опускаются, а пустая строка, False и 0 сохраняются."""

    client.send = MagicMock(return_value=FakeResponse([]))

    assert client.get_deliverypoints(**filters) == []
    client.send.assert_called_once_with("v2/deliverypoints", method="get", params=filters, raise_errors=True)


def test_deliverypoints_forwards_all_filters_and_http_options(client):
    """Все фильтры передаются в query, а HTTP-настройки отдельно передаются в send."""

    client.send = MagicMock(return_value=FakeResponse([]))
    filters = {
        "country_code": "RU",
        "region_code": 77,
        "have_cashless": False,
        "have_cash": True,
        "allowed_cod": False,
        "is_dressing_room": True,
        "weight_max": 0,
        "weight_min": 1,
        "lang": "rus",
        "take_only": False,
        "is_handout": True,
    }

    client.get_deliverypoints(101000, 44, "PVZ", **filters, raise_errors=False, timeout=7, headers={})

    client.send.assert_called_once_with(
        "v2/deliverypoints",
        method="get",
        params={"postal_code": 101000, "city_code": 44, "type": "PVZ", **filters},
        raise_errors=False,
        timeout=7,
        headers={},
    )


def test_deliverypoints_returns_original_response(client):
    """origin_response=True возвращает HTTP-ответ без декодирования JSON."""

    raw_response = MagicMock()
    client.send = MagicMock(return_value=raw_response)

    assert client.get_deliverypoints(origin_response=True) is raw_response
    raw_response.json.assert_not_called()


@pytest.mark.parametrize("origin_response", [True, False])
@pytest.mark.parametrize("raise_errors", [True, False])
@responses.activate
def test_deliverypoints_http_errors(authorized_test_client, origin_response, raise_errors):
    """HTTP-ошибка вызывает исключение либо возвращается в выбранном формате при отключённой проверке."""

    error = {"errors": [{"code": "invalid", "message": "Invalid filter"}]}
    responses.add(responses.GET, f"{API_URL}v2/deliverypoints", json=error, status=400)

    if raise_errors:
        with pytest.raises(CdekRequestException) as exc_info:
            authorized_test_client.get_deliverypoints(origin_response=origin_response)
        assert exc_info.value.response.status_code == 400
        assert exc_info.value.response.json() == error
    else:
        result = authorized_test_client.get_deliverypoints(raise_errors=False, origin_response=origin_response)
        if origin_response:
            assert result.status_code == 400
            assert result.json() == error
        else:
            assert result == error
