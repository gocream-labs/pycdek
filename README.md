<h1 align="center" style="font-size:42px;font-weight:700;vertical-align:middle;" >
	<img src="https://raw.githubusercontent.com/gocream-labs/.github/master/branding/logo.png" alt="GoCream Labs" width="auto" height="42px" style="height:42px;vertical-align:middle;" />
	×
	<img src="https://raw.githubusercontent.com/gocream-labs/pycdek/master/logo.svg" alt="CDEK" width="auto" height="42px" style="height:42px;vertical-align:middle;" />
</h1>

<p align="center">
	<a href="https://pypi.org/project/gocream-pycdek">
		<img src="https://img.shields.io/pypi/status/gocream-pycdek.svg" alt="PyPI - Status" />
	</a>
	<a href="https://pypi.org/project/gocream-pycdek">
		<img src="https://img.shields.io/pypi/v/gocream-pycdek.svg" alt="PyPI - Version" />
	</a>
	<a href="https://pypi.org/project/gocream-pycdek">
		<img src="https://img.shields.io/pypi/dm/gocream-pycdek.svg" alt="PyPI - Downloads" />
	</a>
	<a href="https://pypi.org/project/gocream-pycdek">
		<img src="https://img.shields.io/pypi/pyversions/gocream-pycdek.svg" alt="PyPI - Python Version" />
	</a>
</p>
<p align="center">
	<a href="https://github.com/gocream-labs/pycdek/actions/workflows/ci.yml" >
		<img src="https://img.shields.io/github/actions/workflow/status/gocream-labs/pycdek/ci.yml?branch=master&logo=github&label=tests" alt="Tests - Running" />
	</a>
	<a href="https://codecov.io/gh/gocream-labs/pycdek" >
		<img src="https://img.shields.io/codecov/c/github/gocream-labs/pycdek?logo=codecov&logoColor=white&label=coverage" alt="Coverage" />
	</a>
</p>
<p align="center">
	<a href="https://github.com/pypa/hatch" target="_blank">
		<img src="https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg" alt="Hatch project" />
	</a>
	<a href="https://gitmoji.dev" target="_blank">
		<img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg" alt="Gitmoji" />
	</a>
	<a href="https://squidfunk.github.io/mkdocs-material/" target="_blank">
		<img src="https://img.shields.io/badge/-Material_for_MkDocs-526CFE?logo=MaterialForMkDocs&logoColor=white&labelColor=gray" alt="Built with Material for MkDocs" />
	</a>
	<a href="https://github.com/astral-sh/ruff" target="_blank">
		<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="linting - Ruff" />
	</a>
	<a href="https://raw.githubusercontent.com/gocream-labs/pycdek/master/LICENSE" target="_blank">
		<img src="https://img.shields.io/pypi/l/gocream-pycdek" alt="License - Mozilla Public License Version 2.0" />
	</a>
</p>

<p align="center">
	<b>Документация: <a href="https://gocream-labs.github.io/pycdek/">gocream-labs.github.io/pycdek</a></b>
</p>

`gocream-pycdek` — Python-библиотека для работы с [CDEK API v2.0](https://apidoc.cdek.ru/).


## Установка

```sh
pip install gocream-pycdek
```

Стабильной версии пока нет, поэтому команда выше поставит последний release
candidate. После выхода 2.0.0 предварительные версии ставятся флагом `--pre`:

```sh
pip install --pre gocream-pycdek
```

Импорт в Python выполняется через пакет `gocream_pycdek`:

```python
from gocream_pycdek import CdekClient
from gocream_pycdek import ContractType

client = CdekClient(
    "client-id",
    "client-secret",
    contract_type=ContractType.ONLINE_STORE,
)
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


## Статус проекта

Библиотека находится в процессе актуализации. До выхода стабильной версии 2.0.0
публичный API бета-версий может изменяться.


## Дополнительные материалы

- [Справочник публичного API](https://gocream-labs.github.io/pycdek/latest/api/)
- [Известные проблемы](https://gocream-labs.github.io/pycdek/latest/known-issues/)
- [План развития](https://gocream-labs.github.io/pycdek/latest/roadmap/)
- [Участие в разработке](https://gocream-labs.github.io/pycdek/latest/contributing/)
- [Процесс релиза и версионирования](https://gocream-labs.github.io/pycdek/latest/releasing/)
- [История изменений](https://gocream-labs.github.io/pycdek/latest/changelog/)
- [Официальная документация CDEK API](https://apidoc.cdek.ru/)


## Лицензия

Проект распространяется по [лицензии MPL-2.0](https://www.mozilla.org/MPL/2.0/).
