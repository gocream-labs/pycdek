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
hatch run mtest:check      # матрица Python 3.10–3.14
hatch version              # текущая версия
hatch build                # sdist + wheel
```

До отдельного коммита с форматированием `lint:fmt-check` может быть красным:
он меняет ручное выравнивание в справочниках и стиль части `client.py`. Такие
изменения нужно делать отдельным коммитом и добавлять его SHA в
`.git-blame-ignore-revs`. До этого в CI достаточно `lint:check`.


## Branches and Pull Requests

Используется [GitHub Flow][github_flow]: одна основная долгоживущая ветка,
изменения вносятся через pull request. Перед отправкой PR:

1. Опишите, что изменилось и зачем.
2. Добавьте или обновите тесты.
3. Запустите проверки из раздела выше.
4. Отдельно отметьте изменения публичного API и совместимости.


## Commits

Коммиты имеют формат gitmoji со скоупом:

```text
✨ (client): Add order update method
🐛 (utils): Fix clear_dict on nested lists
🎨 (style): Format code with Ruff
```

Формат влияет на версию следующего релиза и CHANGELOG. Поэтому сообщения
коммитов должны соответствовать ему; `🎨` и `:art:` допустимы для
форматирования и не повышают версию. `hatch run init` устанавливает хуки:
Ruff проверяет staged Python-файлы перед коммитом, а gitlint проверяет форму
заголовка коммита.


## Important Considerations

До релиза 2.0.0 сначала фиксируем текущее поведение тестами, даже если оно
кажется ошибочным. Исправления, меняющие публичный контракт или данные,
отправляемые в API, относятся к плану 3.0.0 и должны быть явно описаны в PR.

[hatch]: https://hatch.pypa.io/
[github_flow]: https://docs.github.com/en/get-started/using-github/github-flow
