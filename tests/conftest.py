"""Общие фикстуры клиентов для тестов API-клиента."""

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
