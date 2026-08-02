# GoCream PyCDEK

`gocream-pycdek` — Python-библиотека для работы с CDEK API v2.0.

## Установка

```sh
pip install gocream-pycdek
```

Для установки предварительной версии укажите её явно:

```sh
pip install gocream-pycdek==2.0.0b10
```

## Быстрый старт

```python
from gocream_pycdek.client import CDEKApiClient


client = CDEKApiClient(
    id="client-id",
    secret="client-secret",
    is_shop=True,
)

regions = client.get_regions()
```

Параметр `production=False` переключает клиент на тестовый контур СДЭК.

## Дополнительные материалы

- [Справочник публичного API](api.md)
- [Известные проблемы](known-issues.md)
- [Процесс выпуска версий](releasing.md)
- [История изменений](https://github.com/gocream/pycdek/blob/master/CHANGELOG.md)
- [Официальная документация CDEK API](https://apidoc.cdek.ru/)
