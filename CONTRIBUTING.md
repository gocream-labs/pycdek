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
hatch run docs:build       # строгая сборка документации
hatch run docs:links       # проверка внутренних ссылок
hatch run docs:serve       # локальный сервер документации
hatch run docs:versions    # список опубликованных версий документации
hatch version              # текущая версия
hatch build --clean        # чистая сборка sdist + wheel
```


## Branches and Pull Requests

Используется [GitHub Flow][github_flow]: одна основная долгоживущая ветка,
изменения вносятся через pull request. Перед отправкой PR:

1. Опишите, что изменилось и зачем.
2. Добавьте или обновите тесты.
3. Запустите проверки из раздела выше.
4. Отдельно отметьте изменения публичного API и совместимости.


## Commits

Коммиты имеют формат [gitmoji](https://gitmoji.dev/) со скоупом:

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

!!! note
	Для создания сообщений коммитов удобно использовать
    [gitmoji-cli](https://github.com/carloscuesta/gitmoji-cli).


## Important Considerations

До релиза 2.0.0 сначала фиксируем текущее поведение тестами, даже если оно
кажется ошибочным. Исправления, меняющие публичный контракт или данные,
отправляемые в API, относятся к плану 3.0.0 и должны быть явно описаны в PR.


[hatch]: https://hatch.pypa.io/
[github_flow]: https://docs.github.com/en/get-started/using-github/github-flow
