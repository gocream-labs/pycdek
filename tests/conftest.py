"""Общие фикстуры клиентов и ответов для тестов API-клиента."""

from copy import deepcopy
from datetime import datetime
from datetime import timedelta
import json
from pathlib import Path

import pytest

from gocream_pycdek.client import CDEKApiClient


@pytest.fixture
def client():
    """Клиент интернет-магазина с тестовыми credentials и production URL."""
    return CDEKApiClient("client-id", "client-secret", is_shop=True)


@pytest.fixture
def delivery_client():
    """Клиент договора доставки для проверки development URL."""
    return CDEKApiClient("client-id", "client-secret", is_shop=False, production=False)


@pytest.fixture
def test_client():
    """Клиент интернет-магазина с URL тестового контура CDEK."""
    return CDEKApiClient("client-id", "client-secret", is_shop=True, production=False)


@pytest.fixture
def authorized_client(client):
    """Клиент с действующим тестовым токеном для endpoint-level HTTP-тестов."""
    client._token = "token"
    client._token_exp = datetime.now() + timedelta(hours=1)
    return client


@pytest.fixture
def authorized_test_client(test_client):
    """Клиент тестового контура с действующим тестовым токеном."""
    test_client._token = "token"
    test_client._token_exp = datetime.now() + timedelta(hours=1)
    return test_client


@pytest.fixture
def api_response():
    """Возвращает независимую копию ответа тестового контура CDEK."""
    fixtures_path = Path(__file__).parent / "fixtures" / "api_edu"

    def load(name):
        fixture_path = fixtures_path / f"{name}.json"
        response = json.loads(fixture_path.read_text(encoding="utf-8"))
        return deepcopy(response)

    return load


@pytest.fixture
def api_response_text():
    """Возвращает текстовый ответ тестового контура CDEK."""
    fixtures_path = Path(__file__).parent / "fixtures" / "api_edu"

    def load(name, suffix="xml"):
        return (fixtures_path / f"{name}.{suffix}").read_text(encoding="utf-8").rstrip("\n")

    return load
