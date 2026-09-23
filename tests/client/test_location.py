"""Тесты справочников регионов и городов, включая постраничный обход."""

from unittest.mock import MagicMock
from unittest.mock import call

import pytest
import responses

from gocream_pycdek.exceptions import CdekRequestException
from tests.helpers import FakeResponse
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"


# Контрактные тесты: `send` замокан, сети нет.


def test_get_regions_returns_decoded_response(client):
    """Проверяет параметры и декодированный ответ справочника регионов."""

    client.send = MagicMock(return_value=FakeResponse([{"code": 1}]))
    assert client.get_regions(country_codes=["RU"], page=0) == [{"code": 1}]
    client.send.assert_called_once_with(
        "v2/location/regions",
        method="get",
        params={"country_codes": ["RU"], "size": 1000, "page": 0},
        raise_errors=True,
    )


def test_get_cities_returns_decoded_response(client):
    """Проверяет параметры и декодированный ответ справочника городов."""

    client.send = MagicMock(return_value=FakeResponse([{"code": 1}]))
    assert client.get_cities(city="Moscow") == [{"code": 1}]
    client.send.assert_called_once_with(
        "v2/location/cities",
        method="get",
        params={"city": "Moscow", "page": 0, "size": 1000},
        raise_errors=True,
    )


@pytest.mark.parametrize(
    ("all_method_name", "page_method_name"),
    [
        ("get_all_regions", "get_regions"),
        ("get_all_cities", "get_cities"),
    ],
    ids=["regions", "cities"],
)
def test_pagination_generators_reset_page_and_stop_on_empty(client, all_method_name, page_method_name):
    """Проверяет сброс страницы, последовательный обход страниц и остановку на пустом ответе."""

    page_method = MagicMock(side_effect=[[{"code": 1}], [{"code": 2}], []])
    setattr(client, page_method_name, page_method)

    assert list(getattr(client, all_method_name)(page=99)) == [{"code": 1}, {"code": 2}]
    assert page_method.call_args_list == [
        call(page=0, origin_response=False),
        call(page=1, origin_response=False),
        call(page=2, origin_response=False),
    ]


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_get_regions_endpoint(authorized_test_client):
    """Проверяет query-параметры справочника регионов и разбор ответа контура."""

    resp_json = recorded_response("regions")
    responses.add(responses.GET, f"{API_URL}v2/location/regions", json=resp_json, status=200)

    request_params = {"country_codes": ["RU"], "size": 2, "page": 0}

    result = authorized_test_client.get_regions(**request_params)

    sent = only_request(responses.calls)

    assert sent.params == {"country_codes": "RU", "size": "2", "page": "0"}
    assert result == resp_json


@responses.activate
def test_get_cities_endpoint(authorized_test_client):
    """Проверяет query-параметры справочника городов и разбор ответа контура."""

    resp_json = recorded_response("cities")
    responses.add(responses.GET, f"{API_URL}v2/location/cities", json=resp_json, status=200)

    request_params = {"city": "Москва", "size": 2, "page": 0}

    result = authorized_test_client.get_cities(**request_params)

    sent = only_request(responses.calls)

    assert sent.params == {"city": "Москва", "size": "2", "page": "0"}
    assert result == resp_json


@pytest.mark.parametrize("kind", ["regions", "cities"])
def test_location_preserves_explicit_filters_and_request_options(client, kind):
    """Фильтры теряют только None; HTTP-настройки передаются отдельно в `send`."""

    client.send = MagicMock(return_value=FakeResponse([]))
    filters = {
        "country_codes": ["RU", "KZ"],
        "region_code": "",
        "kladr_region_code": "77",
        "fias_region_guid": "region-guid",
        "size": None,
        "page": 0,
        "lang": "rus",
    }
    if kind == "cities":
        filters.update(
            kladr_code="7700000000000", fias_guid="city-guid", postal_code="101000", code=44, city="", payment_limit=0
        )

    assert getattr(client, f"get_{kind}")(**filters, raise_errors=False, timeout=7, headers={}) == []

    client.send.assert_called_once_with(
        f"v2/location/{kind}",
        method="get",
        params={key: value for key, value in filters.items() if key != "size"},
        raise_errors=False,
        timeout=7,
        headers={},
    )


@pytest.mark.parametrize("kind", ["regions", "cities"])
def test_location_returns_original_response(client, kind):
    """При origin_response=True метод возвращает HTTP-ответ без декодирования."""

    raw_response = MagicMock()
    client.send = MagicMock(return_value=raw_response)

    assert getattr(client, f"get_{kind}")(origin_response=True) is raw_response
    raw_response.json.assert_not_called()


@pytest.mark.parametrize("kind", ["regions", "cities"])
@pytest.mark.parametrize("raise_errors", [True, False])
@responses.activate
def test_location_http_errors(authorized_test_client, kind, raise_errors):
    """HTTP-ошибки вызывают исключение либо возвращаются декодированными при raise_errors=False."""

    error = {"errors": [{"code": "invalid", "message": "Invalid filter"}]}
    responses.add(responses.GET, f"{API_URL}v2/location/{kind}", json=error, status=400)

    if raise_errors:
        with pytest.raises(CdekRequestException) as exc_info:
            getattr(authorized_test_client, f"get_{kind}")()
        assert exc_info.value.response.status_code == 400
        assert exc_info.value.response.json() == error
    else:
        assert getattr(authorized_test_client, f"get_{kind}")(raise_errors=False) == error


@pytest.mark.parametrize("kind", ["regions", "cities"])
def test_location_pagination_is_lazy_and_preserves_http_objects(client, kind):
    """Обход ленивый, сохраняет фильтры и HTTP-объекты, переопределяя page и origin_response."""

    hook = MagicMock()
    options = {"country_codes": ["RU"], "size": 1, "page": 99, "origin_response": True, "hooks": {"response": hook}}
    page_method = MagicMock(side_effect=[[{"code": 1}], []])
    setattr(client, f"get_{kind}", page_method)

    result = getattr(client, f"get_all_{kind}")(**options)
    page_method.assert_not_called()
    assert list(result) == [{"code": 1}]
    assert page_method.call_args_list == [
        call(country_codes=["RU"], size=1, page=0, origin_response=False, hooks={"response": hook}),
        call(country_codes=["RU"], size=1, page=1, origin_response=False, hooks={"response": hook}),
    ]
    assert page_method.call_args.kwargs["hooks"]["response"] is hook
    assert options["page"] == 99
    assert options["origin_response"] is True


@pytest.mark.parametrize("kind", ["regions", "cities"])
@responses.activate
def test_location_pagination_stops_on_http_error(authorized_test_client, kind):
    """При ошибке следующей страницы обход прекращается с исключением, не выдавая ключи ошибки."""

    url = f"{API_URL}v2/location/{kind}"
    responses.add(responses.GET, url, json=[{"code": 1}], status=200)
    responses.add(responses.GET, url, json={"errors": [{"code": "invalid"}]}, status=400)

    result = getattr(authorized_test_client, f"get_all_{kind}")()
    assert next(result) == {"code": 1}
    with pytest.raises(CdekRequestException):
        next(result)
    assert [request.request.params["page"] for request in responses.calls] == ["0", "1"]
