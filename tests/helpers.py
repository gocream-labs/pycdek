"""Хелперы тестов: записанные ответы контура и разбор ушедшего запроса.

Это обычные функции, а не фикстуры: состояния теста они не держат и от него не
зависят. Фикстурами остались только клиенты - у них есть своё на каждый тест
состояние: токен и HTTP-сессия.
"""

import json
from pathlib import Path


RECORDINGS_PATH = Path(__file__).parent / "fixtures" / "api_edu"


class FakeResponse:
    """Минимальная замена `requests.Response` для тестов преобразования ответа."""

    def __init__(self, body=None, content=b"file"):
        self.body = body
        self.content = content

    def json(self):
        return self.body


def recorded_response(name):
    """Читает записанный JSON-ответ тестового контура CDEK по имени файла.

    `recorded_response("order_create")` - это `tests/fixtures/api_edu/order_create.json`,
    снятый с `api.edu.cdek.ru`; происхождение каждого файла описано в `manifest.json`
    рядом с ними. Файл читается на каждый вызов, поэтому полученное дерево можно
    править, не задевая соседние тесты.
    """

    return json.loads((RECORDINGS_PATH / f"{name}.json").read_text(encoding="utf-8"))


def only_request(calls):
    """Достаёт единственный запрос из записанных `responses.calls`.

    Токен у `authorized_*` клиентов проставлен заранее, поэтому за авторизацией
    запрос не уходит и записанный вызов остаётся единственным. Если вызовов
    окажется больше, молча смотреть на первый было бы неверно - функция падает.

    Args:
        calls: `responses.calls` - записанные вызовы активного мока.

    Returns:
        Отправленный `PreparedRequest`: `url`, `method`, `params`, `headers`, `body`.
    """

    assert len(calls) == 1, f"ожидался один запрос, записано {len(calls)}"

    return calls[0].request


def json_body(request):
    """Декодирует JSON-тело отправленного запроса."""

    return json.loads(request.body)
