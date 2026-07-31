<img alt="CDEK" src="/logo.svg" width="150" height="auto" />

# PyCDEK 2

Python-библиотека для CDEK API v2.0.

Документация API: [на русском][api_url_ru] и [на английском][api_url_en].


## Installation

```sh
pip install pycdek-2
```

Импорт в Python выполняется через `pycdek`:

```python
from pycdek.client import CDEKApiClient
```


## Project Status

Библиотека находится в процессе актуализации. Версия 2.0.0 сохраняет публичное
API текущей беты `2.0.0b9`, а версия 3.0.0 будет содержать ломающие изменения.

- [План работ](ROADMAP.md)
- [Известные проблемы](docs/known-issues.md)
- [Руководство для контрибьюторов](CONTRIBUTING.md)
- [Процесс релиза и версионирования](docs/releasing.md)


## License

Проект распространяется по [лицензии MPL-2.0][mpl].

[api_url_ru]: https://api-docs.cdek.ru/29923741.html
[api_url_en]: https://api-docs.cdek.ru/33828739.html
[mpl]: https://www.mozilla.org/MPL/2.0/
