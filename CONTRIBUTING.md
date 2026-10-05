# Contributing

Раздел описывает работу над библиотекой: настройку окружения, ветки, формат коммитов и оформление pull request. Выпуск и публикация версий описаны отдельно, в разделе документации [**Releasing**](https://gocream-labs.github.io/pycdek/next/releasing/).

Общий порядок работы:

1. создайте рабочую ветку от актуальной `next`;
2. внесите изменения и покройте их тестами;
3. оформите коммиты в формате gitmoji со скоупом;
4. прогоните локальные проверки;
5. отправьте pull request в `next` и дождитесь CI и review.


## Local Setup

Проект использует [Hatch][hatch]: окружения создаются автоматически при первом запуске команды, отдельно устанавливать зависимости не нужно.

Настройка локального репозитория:

```sh
hatch run init
```

Команда подключает `.git-blame-ignore-revs` к `git blame` и устанавливает git-хуки: перед коммитом запускается статический анализ Ruff, а gitlint проверяет форму заголовка сообщения. Отменяет настройку `hatch run remove`.

Код и тесты:

| Команда | Назначение |
|---|---|
| `hatch run lint:check` | статический анализ |
| `hatch run lint:fmt-check` | проверка форматирования |
| `hatch run lint:format` | автоисправление и форматирование |
| `hatch run test:check` | тесты с покрытием на основной версии Python |
| `hatch run mtest:check` | матрица тестов Python 3.10–3.14, отчёт `coverage.xml` для Codecov |

Документация:

| Команда | Назначение |
|---|---|
| `hatch run docs:build` | строгая сборка документации |
| `hatch run docs:links` | проверка внутренних ссылок в собранном сайте |
| `hatch run docs:serve` | локальный сервер документации |
| `hatch run docs:versions` | список опубликованных версий документации |

Пакет:

| Команда | Назначение |
|---|---|
| `hatch version` | текущая версия пакета |
| `hatch build --clean` | чистая сборка sdist + wheel |

!!! note
	`docs:links` проверяет уже собранный сайт в каталоге `site/`, поэтому запускайте её после `docs:build`.


## Docstrings

Docstring пишутся в [Google-style][google-style] на русском языке. Справочник API собирается из них автоматически: `mkdocstrings-python` настроен на `docstring_style: google` в `mkdocs.yml`, страница [**Справочник API**](https://gocream-labs.github.io/pycdek/next/api/) содержит только директивы `:::`, а текст берётся из кода.

Разделы - стандартные Google-секции `Args:`, `Returns:`, `Raises:`, `Yields:`, `Examples:`, а для атрибутов класса - `Attributes:` в его docstring (`Args:` там означала бы параметры конструктора, а они описываются в `__init__`). Типы в секциях не дублируются: они берутся из аннотаций. Внутри docstring работает Markdown-разметка Material for MkDocs - списки, ссылки, `admonition`, блоки кода:

```python
def get_order(self, order_uuid: str) -> dict:
	"""Возвращает заказ по идентификатору CDEK.

	Args:
		order_uuid: Идентификатор заказа в системе CDEK.

	Returns:
		Ответ API с данными заказа.

	Raises:
		CdekRequestException: Если API вернул ошибку.
	"""
```

Ссылки на другие объекты библиотеки и на стандартную библиотеку Python оформляются как `[CdekRequestException][gocream_pycdek.exceptions.CdekRequestException]` - перекрёстные ссылки включены (`signature_crossrefs`), inventory Python подключён.

!!! note
	Старые docstring приводятся к Google-style постепенно, отдельным этапом роадмапа, поэтому предупреждения парсера в `mkdocs.yml` пока отключены (`docstring_options.warnings: false`). Новый и изменяемый код пишется сразу в целевом формате.


## Branches

В проекте две долгоживущие ветки:

- `next` - ветка для RC-релизов и соответствующей документации;
- `master` - ветка стабильных релизов.

Рабочую ветку создавайте от актуальной `next`:

```sh
git switch next
git pull --ff-only
git switch -c feature/order-update
```

Для названия используйте короткий префикс по типу изменения, например `feature/`, `fix/`, `docs/` или `refactor/`.

Готовые изменения возвращаются в `next` через pull request; напрямую в `master` они не отправляются. При необходимости beta-версию можно вручную выпустить из рабочей ветки до её merge в `next`.


## Commits

Заголовок коммита состоит из emoji-маркера [gitmoji](https://gitmoji.dev/), скоупа и краткого описания:

```text
✨ (client): Add order update method
🐛 (utils): Fix clear_dict on nested lists
🎨 (style): Format code with Ruff
```

Формат обязателен: по маркеру определяются версия следующего релиза и раздел в `CHANGELOG.md`. Маркеры `🎨` (форматирование), `🧪` (тесты) и `📄` (лицензия) попадают в changelog, но версию не повышают.

Полный список маркеров, изменяющих версию, находится в секции `[tool.semantic_release.commit_parser_options]` файла `pyproject.toml`. Маркер вне этого списка попадёт в раздел `Other`; как добавить новый, описано в разделе документации [**Releasing**](https://gocream-labs.github.io/pycdek/next/releasing/#changelog).

!!! note
	Для создания сообщений коммитов удобно использовать [gitmoji-cli](https://github.com/carloscuesta/gitmoji-cli).


## Pull Requests

Обычные изменения отправляются pull request в `next`. Pull request в `master` создаётся только для стабильного релиза; имя исходной ветки не ограничено, а предварительный beta- или RC-релиз необязателен.

Перед отправкой PR:

1. Запустите проверки из раздела **Local Setup**: как минимум `lint:check`, `lint:fmt-check` и `test:check`, а при правках документации - `docs:build` и `docs:links`.
2. Добавьте или обновите тесты.
3. Опишите, что изменилось и зачем.
4. Отдельно отметьте изменения публичного API и совместимости.

После успешного CI pull request должен пройти review. Дальнейшие шаги для beta и стабильной версии описаны в разделе документации [**Releasing**](https://gocream-labs.github.io/pycdek/next/releasing/).


[hatch]: https://hatch.pypa.io/
[google-style]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
