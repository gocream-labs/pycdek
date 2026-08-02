<img alt="CDEK" src="/logo.svg" width="150" height="auto" />

# GoCream PyCDEK

Python-библиотека для CDEK API v2.0.

Документация API: [портал документации СДЭК][api_url].


## Installation

```sh
pip install gocream-pycdek
```

Импорт в Python выполняется через `gocream_pycdek`:

```python
from gocream_pycdek import CdekClient
from gocream_pycdek import ContractType

client = CdekClient(
    "client-id",
    "client-secret",
    contract_type=ContractType.ONLINE_STORE,
)
```


## Project Status

Библиотека находится в процессе актуализации. До выхода стабильной версии 2.0.0
публичный API бета-версий может изменяться.

- [План работ](ROADMAP.md)
- [Известные проблемы](docs/known-issues.md)
- [Руководство для контрибьюторов](CONTRIBUTING.md)
- [Процесс релиза и версионирования](docs/releasing.md)


## License

Проект распространяется по [лицензии MPL-2.0][mpl].

[api_url]: https://apidoc.cdek.ru/
[mpl]: https://www.mozilla.org/MPL/2.0/
