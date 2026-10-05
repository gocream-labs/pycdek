"""Регрессионные тесты наблюдаемого поведения из списка известных проблем."""

from pathlib import PurePosixPath


def test_get_url_mangles_absolute_url_passed_as_path(client):
    """Фиксирует порчу абсолютной ссылки, переданной как `PurePath`.

    `as_posix()` схлопывает `//` в схеме до одного слэша, проверка на `https://`
    не срабатывает, и ссылка молча приклеивается к базовому адресу CDEK.
    """

    result = client.get_url(PurePosixPath("https://files.example/waybill.pdf"))

    assert result == "https://api.cdek.ru/https:/files.example/waybill.pdf"
