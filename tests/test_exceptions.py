"""Проверки публичного контракта исключений библиотеки."""

from types import SimpleNamespace

import pytest
from requests import RequestException

from gocream_pycdek.exceptions import BaseCdekException
from gocream_pycdek.exceptions import CdekApiAccessException
from gocream_pycdek.exceptions import CdekApiWrongTokenTypeException
from gocream_pycdek.exceptions import CdekRequestException


@pytest.mark.parametrize(
    ("exception", "code", "message"),
    [
        (BaseCdekException(), "base_cdek_exception", "Base CDEK exception."),
        (CdekApiAccessException(), "cdek_bad_api_credentials", "CDEK bad api credentials."),
        (
            CdekApiWrongTokenTypeException("Basic"),
            "cdek_api_token_type",
            "CDEK api returned token type `Basic` that not supported.",
        ),
    ],
    ids=["base", "access", "wrong-token-type"],
)
def test_exception_contract(exception, code, message):
    """Проверяет стабильные code/message и строковое представление исключений."""

    assert exception.code == code
    assert exception.message == message
    assert str(exception) == f"Error {code}: {message}"


def test_request_exception_is_a_requests_exception():
    """Проверяет совместимость обёртки с `requests.RequestException`."""

    error = CdekRequestException()
    assert isinstance(error, RequestException)
    assert error.response is None
    assert error.request is None


def test_request_exception_carries_response_and_request():
    """Проверяет, что обёртка отдаёт ответ и запрос как обычное исключение `requests`."""

    response = SimpleNamespace(status_code=503, request="request-object")
    error = CdekRequestException("503 Server Error", response=response)

    assert error.response is response
    assert error.request == "request-object"
    assert str(error) == "Error cdek_request_exception: 503 Server Error"


def test_request_exception_prefers_explicit_request():
    """Проверяет приоритет явно переданного запроса над запросом из ответа."""

    response = SimpleNamespace(status_code=503, request="from-response")
    error = CdekRequestException(response=response, request="explicit")

    assert error.request == "explicit"
