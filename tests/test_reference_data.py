"""Smoke-тесты справочников тарифов, услуг, статусов и кодов API."""

import pytest

import gocream_pycdek.currency as currency
import gocream_pycdek.errors as errors
import gocream_pycdek.overships as overships
import gocream_pycdek.services as services
import gocream_pycdek.statuses as statuses
import gocream_pycdek.tariffs as tariffs


def uppercase_values(module):
    """Возвращает публичные константы модуля, исключая служебные имена."""
    return {name: value for name, value in vars(module).items() if name.isupper() and not name.startswith("__")}


@pytest.mark.parametrize(
    "module",
    [currency, errors, overships, services, statuses, tariffs],
    ids=["currency", "errors", "overships", "services", "statuses", "tariffs"],
)
def test_reference_module_exposes_non_empty_constants(module):
    """Проверяет, что каждый справочный модуль импортируется и не пуст."""

    values = uppercase_values(module)
    assert values
    assert all(value not in (None, "") for value in values.values())


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (currency.RUB, 1),
        (services.INSURANCE, "INSURANCE"),
        (overships.LIMITED_LIABILITY_COMPANY, 137),
        (tariffs.IS_REGULAR_DD, 139),
        (statuses.ORDER_DELIVERED, "DELIVERED"),
        (errors.V2_BAD_REQUEST, "v2_bad_request"),
    ],
    ids=["RUB", "INSURANCE", "LIMITED_LIABILITY_COMPANY", "IS_REGULAR_DD", "ORDER_DELIVERED", "V2_BAD_REQUEST"],
)
def test_reference_data_contains_public_contract_value(value, expected):
    """Проверяет ключевые значения публичных справочников по отдельности."""

    assert value == expected
