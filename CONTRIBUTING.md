# Contributing

## Local Setup

Проект использует [Hatch][hatch]. Для настройки локального репозитория:

```sh
hatch run init
```

Основные команды:

```sh
hatch run lint:check       # статический анализ
hatch run lint:fmt-check   # проверка форматирования
hatch run lint:format      # автоисправление и форматирование
hatch run test:check       # тесты с покрытием
hatch run mtest:check      # матрица тестов Python 3.10–3.14
hatch run docs:build       # строгая сборка документации
hatch run docs:links       # проверка внутренних ссылок в документации
hatch run docs:serve       # локальный сервер документации
hatch run docs:versions    # список опубликованных версий документации
hatch version              # текущая версия пакета
hatch build --clean        # чистая сборка sdist + wheel
```


## Branches

В проекте две долгоживущие ветки:

- `next` - основная ветка разработки, RC-релизов и предварительной документации;
- `master` - ветка стабильных релизов.

Рабочую ветку создавайте от актуальной `next`:

```sh
git switch next
git pull --ff-only
git switch -c feature/order-update
```

Для названия используйте короткий префикс по типу изменения, например `feature/`, `fix/`, `docs/` или `refactor/`. Готовые изменения возвращаются в `next` через pull request; напрямую в `master` они не отправляются. При необходимости beta-версию можно вручную выпустить из рабочей ветки до её merge в `next`.


## Commits

Коммиты имеют формат [gitmoji](https://gitmoji.dev/) со скоупом:

```text
✨ (client): Add order update method
🐛 (utils): Fix clear_dict on nested lists
🎨 (style): Format code with Ruff
```

Формат влияет на версию следующего релиза и CHANGELOG. Поэтому сообщения коммитов должны соответствовать ему; `🎨` и `:art:` допустимы для форматирования и не повышают версию. `hatch run init` устанавливает хуки: Ruff проверяет staged Python-файлы перед коммитом, а gitlint проверяет форму заголовка коммита.

Полный список emoji-маркеров, изменяющих версию, находится в секции `[tool.semantic_release.commit_parser_options]` файла `pyproject.toml`.

!!! note
    Для создания сообщений коммитов удобно использовать [gitmoji-cli](https://github.com/carloscuesta/gitmoji-cli).


## Pull Requests

Обычные изменения отправляются pull request в `next`. Pull request в `master` создаётся только для стабильного релиза; имя исходной ветки не ограничено, а предварительный beta- или RC-релиз необязателен.

Перед отправкой PR:

1. Опишите, что изменилось и зачем.
2. Добавьте или обновите тесты.
3. Запустите проверки из раздела **Local Setup**.
4. Отдельно отметьте изменения публичного API и совместимости.

После успешного CI pull request должен пройти review. Дальнейшие шаги для beta и стабильной версии описаны в разделе документации [**Releasing**](https://gocream.github.io/pycdek/next/releasing/).


[hatch]: https://hatch.pypa.io/
