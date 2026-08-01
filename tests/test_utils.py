"""Тесты чистых функций очистки данных и legacy-подписи калькулятора."""

import pytest

from gocream_pycdek.utils import clear_dict
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


def test_get_secure_matches_v1_signature():
    """Фиксирует точный MD5-контракт устаревшего калькулятора v1."""

    assert get_secure("secret", "2024-01-02") == "eb283b4d696ab2906670ebc76c47703c"
