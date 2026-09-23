"""Тесты печатных форм - квитанций, штрихкодов и скачивания файлов."""

from io import BytesIO
from unittest.mock import MagicMock

import pytest
import responses

from gocream_pycdek.exceptions import CdekRequestException
from tests.helpers import FakeResponse
from tests.helpers import json_body
from tests.helpers import only_request
from tests.helpers import recorded_response


API_URL = "https://api.edu.cdek.ru/"
ORDER_UUID = "11111111-1111-4111-8111-111111111111"
RECEIPT_UUID = "33333333-3333-4333-8333-333333333333"
BARCODE_UUID = "44444444-4444-4444-8444-444444444444"


# Контрактные тесты: `send` замокан, сети нет.


@pytest.mark.parametrize("method_name", ["request_receipt", "request_barcode"])
def test_request_document_extracts_entity(client, method_name):
    """Проверяет извлечение `entity` при запросе квитанции и штрихкода."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"id": 1}}))
    assert getattr(client, method_name)([{"order_uuid": "u"}]) == {"id": 1}


@pytest.mark.parametrize("method_name", ["get_receipt", "get_barcode"])
def test_get_document_extracts_entity(client, method_name):
    """Проверяет извлечение `entity` при получении квитанции и штрихкода."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"id": 1}}))
    assert getattr(client, method_name)("u") == {"id": 1}


@pytest.mark.parametrize("method_name", ["get_receipt", "get_barcode"])
def test_get_document_preserves_original_response(client, method_name):
    """Проверяет контракт `origin_response=True` при получении квитанции и штрихкода."""

    raw_response = FakeResponse({"entity": {"id": 1}})
    client.send = MagicMock(return_value=raw_response)
    assert getattr(client, method_name)("u", origin_response=True) is raw_response


def test_download_returns_bytes_io(client):
    """Проверяет преобразование содержимого скачанного файла в `BytesIO`."""

    client.send = MagicMock(return_value=FakeResponse({"ok": True}, b"PDF"))
    result = client.download("https://files.example/doc")
    assert isinstance(result, BytesIO)
    assert result.getvalue() == b"PDF"
    assert result.tell() == 0
    assert result.read() == b"PDF"


def test_download_preserves_original_response(client):
    """Проверяет контракт `origin_response=True` при скачивании файла."""

    raw_response = FakeResponse({"ok": True}, b"PDF")
    client.send = MagicMock(return_value=raw_response)
    assert client.download("https://files.example/doc", origin_response=True) is raw_response


# Endpoint-level тесты: HTTP поверх записанных ответов тестового контура.


@responses.activate
def test_request_receipt_endpoint(authorized_test_client):
    """Проверяет тело POST-запроса квитанции и разбор ответа контура."""

    resp_json = recorded_response("receipt_create")
    responses.add(responses.POST, f"{API_URL}v2/print/orders", json=resp_json, status=202)

    request_data = {"orders": [{"order_uuid": ORDER_UUID}], "copy_count": 2, "type": "tpl_china"}

    result = authorized_test_client.request_receipt(
        request_data["orders"],
        copy_count=request_data["copy_count"],
        form_type=request_data["type"],
    )

    sent = only_request(responses.calls)

    assert json_body(sent) == request_data
    assert result == resp_json["entity"]


@responses.activate
def test_get_receipt_endpoint(authorized_test_client):
    """Проверяет адрес запроса квитанции и разбор ответа контура."""

    resp_json = recorded_response("receipt_get")
    url = f"{API_URL}v2/print/orders/{RECEIPT_UUID}"
    responses.add(responses.GET, url, json=resp_json, status=200)

    result = authorized_test_client.get_receipt(RECEIPT_UUID)

    sent = only_request(responses.calls)

    assert sent.url == url
    assert result == resp_json["entity"]


@responses.activate
def test_request_barcode_endpoint(authorized_test_client):
    """Проверяет тело POST-запроса штрихкода и разбор ответа контура.

    Аргумент `format_type` уходит в поле `format`, поэтому имена в вызове и в теле
    запроса совпадают не полностью.
    """

    resp_json = recorded_response("barcode_create")
    responses.add(responses.POST, f"{API_URL}v2/print/barcodes", json=resp_json, status=202)

    request_data = {"orders": [{"order_uuid": ORDER_UUID}], "format": "A6", "lang": "RUS"}

    result = authorized_test_client.request_barcode(
        request_data["orders"],
        format_type=request_data["format"],
        lang=request_data["lang"],
    )

    sent = only_request(responses.calls)

    assert json_body(sent) == request_data
    assert result == resp_json["entity"]


@responses.activate
def test_get_barcode_endpoint(authorized_test_client):
    """Проверяет адрес запроса штрихкода и разбор ответа контура."""

    resp_json = recorded_response("barcode_get")
    url = f"{API_URL}v2/print/barcodes/{BARCODE_UUID}"
    responses.add(responses.GET, url, json=resp_json, status=200)

    result = authorized_test_client.get_barcode(BARCODE_UUID)

    sent = only_request(responses.calls)

    assert sent.url == url
    assert result == resp_json["entity"]


@responses.activate
def test_download_endpoint(authorized_test_client):
    """Проверяет адрес скачивания печатной формы и содержимое полученного файла."""

    url = "https://files.example/waybill.pdf"
    responses.add(responses.GET, url, body=b"%PDF-test", status=200)

    result = authorized_test_client.download(url)

    sent = only_request(responses.calls)

    assert sent.url == url
    assert result.getvalue() == b"%PDF-test"


@pytest.mark.parametrize(
    ("method_name", "options", "payload"),
    [
        ("request_receipt", {}, {"orders": []}),
        ("request_barcode", {}, {"orders": []}),
        ("request_receipt", {"copy_count": 0, "form_type": ""}, {"orders": [], "copy_count": 0, "type": ""}),
        (
            "request_barcode",
            {"copy_count": 0, "format_type": "", "lang": ""},
            {"orders": [], "copy_count": 0, "format": "", "lang": ""},
        ),
    ],
)
def test_request_document_preserves_explicit_values(client, method_name, options, payload):
    """Создание печатной формы опускает только None, сохраняя явно переданные пустые значения."""

    client.send = MagicMock(return_value=FakeResponse({"entity": {"id": 1}}))
    getattr(client, method_name)([], **options)
    assert client.send.call_args.kwargs["data"] == payload


@pytest.mark.parametrize(
    ("method_name", "args", "resource", "http_method", "extra"),
    [
        (
            "request_receipt",
            ([{"order_uuid": "u"}],),
            "v2/print/orders",
            "post",
            {"data": {"orders": [{"order_uuid": "u"}]}},
        ),
        (
            "request_barcode",
            ([{"order_uuid": "u"}],),
            "v2/print/barcodes",
            "post",
            {"data": {"orders": [{"order_uuid": "u"}]}},
        ),
        ("get_receipt", ("u",), "v2/print/orders/u", "get", {}),
        ("get_barcode", ("u",), "v2/print/barcodes/u", "get", {}),
        ("download", ("https://files.example/doc",), "https://files.example/doc", "get", {}),
    ],
)
def test_document_methods_forward_options_and_return_raw_response(
    client, method_name, args, resource, http_method, extra
):
    """Все операции передают HTTP-настройки и возвращают сырой ответ без декодирования по запросу."""

    raw_response = MagicMock()
    client.send = MagicMock(return_value=raw_response)

    result = getattr(client, method_name)(*args, origin_response=True, raise_errors=False, timeout=7, headers={})

    assert result is raw_response
    raw_response.json.assert_not_called()
    client.send.assert_called_once_with(
        resource, method=http_method, raise_errors=False, timeout=7, headers={}, **extra
    )


@pytest.mark.parametrize(
    ("method_name", "args", "resource", "http_method"),
    [
        ("request_receipt", ([{"order_uuid": "u"}],), "v2/print/orders", responses.POST),
        ("request_barcode", ([{"order_uuid": "u"}],), "v2/print/barcodes", responses.POST),
        ("get_receipt", ("u",), "v2/print/orders/u", responses.GET),
        ("get_barcode", ("u",), "v2/print/barcodes/u", responses.GET),
        ("download", (f"{API_URL}document.pdf",), "document.pdf", responses.GET),
    ],
)
@pytest.mark.parametrize("raise_errors", [True, False])
@responses.activate
def test_document_http_errors(authorized_test_client, method_name, args, resource, http_method, raise_errors):
    """HTTP-ошибки вызывают исключение либо доступны в исходном ответе без обязательного entity."""

    error = {"errors": [{"code": "invalid", "message": "Invalid document"}]}
    responses.add(http_method, f"{API_URL}{resource}", json=error, status=400)

    if raise_errors:
        with pytest.raises(CdekRequestException) as exc_info:
            getattr(authorized_test_client, method_name)(*args)
        assert exc_info.value.response.status_code == 400
        assert exc_info.value.response.json() == error
    else:
        result = getattr(authorized_test_client, method_name)(*args, raise_errors=False, origin_response=True)
        assert result.status_code == 400
        assert result.json() == error


@pytest.mark.parametrize("content", [b"", b"%PDF-\x00\xff\n"])
@responses.activate
def test_download_content_is_ready_to_read(authorized_test_client, content):
    """Скачивание сохраняет пустое или бинарное тело и возвращает поток, готовый к чтению."""

    url = f"{API_URL}document.pdf"
    responses.add(responses.GET, url, body=content, status=200)

    result = authorized_test_client.download(url)

    assert result.tell() == 0
    assert result.read() == content
