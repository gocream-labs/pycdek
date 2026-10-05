"""Тесты чистых функций очистки данных и legacy-подписи калькулятора."""

import pytest

from gocream_pycdek.utils import clear_dict
from gocream_pycdek.utils import drop_none
from gocream_pycdek.utils import get_secure
from gocream_pycdek.utils import is_empty


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, True),
        ((), True),
        ({}, True),
        ("", True),
        (0, False),
        (False, False),
        ([], False),
        (" ", False),
    ],
    ids=["none", "empty-tuple", "empty-dict", "empty-string", "zero", "false", "empty-list", "whitespace"],
)
def test_is_empty_classifies_value(value, expected):
    """Проверяет каждый пустой и значимый false-like вариант отдельно."""

    assert is_empty(value) is expected


def test_drop_none_removes_only_none():
    """Проверяет удаление непереданных параметров без чистки пустых значений."""

    assert drop_none(
        {
            "passed": 0,
            "empty_string": "",
            "empty_dict": {},
            "empty_list": [],
            "not_passed": None,
        }
    ) == {"passed": 0, "empty_string": "", "empty_dict": {}, "empty_list": []}


def test_drop_none_keeps_nested_values_untouched():
    """Проверяет, что вложенные структуры пользователя уходят как есть."""

    nested = {"keep": None, "items": [{"empty": ""}]}

    assert drop_none({"nested": nested}) == {"nested": nested}


def test_clear_dict_removes_empty_values_recursively():
    """Проверяет рекурсивное удаление пустых ключей без удаления нуля и вложенных данных."""

    assert clear_dict(
        {
            "keep": 0,
            "nested": {"keep": "value", "empty": None, "deep": {"empty": {}}},
            "empty": {},
            "none": None,
        }
    ) == {"keep": 0, "nested": {"keep": "value"}}


@pytest.mark.xfail(
    reason="clear_dict не обрабатывает словари внутри списков",
    strict=True,
)
def test_clear_dict_cleans_dicts_inside_lists():
    """Проверяет очистку необязательных полей элемента массива API."""

    value = {"items": [{"keep": 1, "empty": ""}]}
    assert clear_dict(value) == {"items": [{"keep": 1}]}


def test_get_secure_matches_v1_signature():
    """Фиксирует точный MD5-контракт устаревшего калькулятора v1."""

    assert get_secure("secret", "2024-01-02") == "eb283b4d696ab2906670ebc76c47703c"
