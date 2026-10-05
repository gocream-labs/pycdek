"""Фикстуры клиентов для тестов API-клиента.

Фикстурой здесь остаётся только то, у чего есть своё на каждый тест состояние -
токен и HTTP-сессия. Чтение записанных ответов и разбор ушедшего запроса - обычные
функции в `tests/client/helpers.py`.
"""

from datetime import datetime
from datetime import timedelta

import pytest

from gocream_pycdek import TEST_API_URL
from gocream_pycdek import CdekClient


@pytest.fixture
def client():
    """Клиент с тестовыми credentials и production URL."""
    return CdekClient("client-id", "client-secret")


@pytest.fixture
def test_client():
    """Клиент с URL тестового контура CDEK."""
    return CdekClient("client-id", "client-secret", base_url=TEST_API_URL)


@pytest.fixture
def authorized_client(client):
    """Клиент с действующим тестовым токеном для endpoint-level HTTP-тестов."""
    client._token = "token"
    client._token_expires_at = datetime.now() + timedelta(hours=1)
    return client


@pytest.fixture
def authorized_test_client(test_client):
    """Клиент тестового контура с действующим тестовым токеном."""
    test_client._token = "token"
    test_client._token_expires_at = datetime.now() + timedelta(hours=1)
    return test_client
