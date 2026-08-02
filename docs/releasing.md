# Releasing and Versioning

Версионирование следует [SemVer][semver]. Версия хранится литералом в
`gocream_pycdek/__init__.py`: её читает Hatchling, а при релизе изменяет
`python-semantic-release`.

Следующая версия определяется по emoji-маркерам в сообщениях коммитов после
прошлого релизного тега. Их интерпретирует emoji-парсер
`python-semantic-release`: `💥` повышает major, `✨` — minor, остальные
поддерживаемые изменения — patch. Перед стабильным релизом выпускается
предварительная версия. Полный список emoji-маркеров, которые изменяют версию,
задан в секции `[tool.semantic_release.commit_parser_options]` файла
`pyproject.toml`.

## Проверки перед релизом

```sh
hatch run lint:check
hatch run lint:fmt-check
hatch run mtest:check
hatch run docs:build
hatch run docs:links
hatch build --clean
```

`--clean` удаляет содержимое `dist/` перед сборкой. Это не позволяет случайно
опубликовать артефакты предыдущей версии вместе с новыми.

## Переход с 2.0.0b9 на 2.0.0-b.10

Старые beta-теги записаны в PEP 440-формате (`2.0.0b9`), который
`python-semantic-release` не распознаёт как SemVer. Один раз нужно добавить
канонический алиас для последнего старого тега:

```sh
git tag -a 2.0.0-b.9 '2.0.0b9^{}' \
  -m "Canonical SemVer alias for 2.0.0b9"
git push origin 2.0.0-b.9
```

После этого проверка должна вывести `2.0.0-b.10`:

```sh
hatch run release:beta-preview
```

Выпуск beta-версии:

```sh
hatch run release:beta
```

Версия и тег имеют SemVer-вид `2.0.0-b.10`. При сборке Python нормализует их в
PEP 440-вид `2.0.0b10`, поэтому wheel будет называться
`gocream_pycdek-2.0.0b10-py3-none-any.whl`.

## Автоматическая публикация

Workflow `.github/workflows/release.yml` запускается после публикации GitHub
Release. Он:

1. прогоняет тесты на Python 3.10–3.14;
2. собирает чистые `sdist` и `wheel`;
3. передаёт только эти артефакты в отдельный publish-job;
4. публикует их на PyPI через OIDC Trusted Publishing без постоянного API-токена.

Для первой публикации нужно заранее создать pending publisher на PyPI:

| Поле | Значение |
|---|---|
| PyPI project name | `gocream-pycdek` |
| Owner | `gocream` |
| Repository | `pycdek` |
| Workflow | `release.yml` |
| Environment | `pypi` |

В GitHub Settings → Environments нужно создать environment `pypi`. Для него
рекомендуется включить required reviewer, чтобы публикация требовала ручного
подтверждения. После создания тега публикуется GitHub Release с этим тегом — его
событие запускает workflow.

## Документация

Локальная сборка и предпросмотр:

```sh
hatch run docs:build
hatch run docs:links
hatch run docs:serve
```

Документация версионируется с помощью `mike`. Версии в переключателе имеют
формат `major.minor`: релизы `2.0.0-b.10` и `2.0.0` обновляют документацию
`2.0`, а несовместимый релиз `3.0.0` публикуется отдельно как `3.0`.

Посмотреть уже опубликованные версии и локально запустить их общий сайт:

```sh
hatch run docs:versions
hatch run docs:serve-versions
```

Workflow `.github/workflows/docs.yml`:

1. строго собирает документацию и проверяет внутренние ссылки в pull request;
2. после публикации GitHub Release разворачивает его документацию через `mike`;
3. назначает предрелизам алиас `dev`, а стабильным версиям — `latest`;
4. раз в неделю проверяет опубликованный сайт, включая внешние ссылки.

В GitHub Settings → Pages нужно один раз выбрать **Deploy from a branch**,
ветку `gh-pages` и каталог `/ (root)`. Workflow создаст ветку при первом
опубликованном релизе. Для deploy-job также должно быть разрешено создавать
коммиты: Settings → Actions → General → Workflow permissions →
**Read and write permissions**.

Для ручной проверки всех ссылок, включая внешние:

```sh
hatch run docs:links-external
```

Эта команда проверяет уже опубликованный сайт. До первого deploy он ожидаемо
отвечает `404`; локальную сборку без сетевых запросов проверяет `docs:links`.

## Стабильная 2.0.0

PSR не считает старую бету `2.0.0b9` последним стабильным тегом. Для выпуска
именно `2.0.0` после проверки beta/rc нужен явный уровень:

```sh
semantic-release --noop version --major --print
semantic-release version --major
```

`tag_format` не добавляет префикс `v`, следуя текущей конвенции тегов. История
до `2.0.0b9` внесена в `CHANGELOG.md` вручную, потому что старые коммиты не
соответствуют текущему gitmoji-формату.

[semver]: https://semver.org/lang/ru/
