# Releasing

Релизы выполняются через GitHub Actions. Разработчику не нужно вручную менять версию и `CHANGELOG.md`, создавать тег или загружать пакет в PyPI.


## Release Flow

| Channel | Source | Trigger | Result |
|---|---|---|---|
| Beta | Любая рабочая ветка, кроме `master` и `next` | Ручной запуск **Prerelease** | `2.0.0-b.N` |
| RC | `next` | Push с изменением версии | `2.0.0-rc.N` |
| Stable | Любая ветка | Merge pull request в `master` | `2.0.0` |

Необходимость новой версии и её уровень определяются по emoji-маркерам в коммитах. Если после предыдущего релиза нет подходящего маркера, workflow завершится без публикации. Правила описаны в разделе [Commits](contributing.md#commits).

Для публикации в PyPI настройте environment `pypi` в GitHub и два Trusted Publisher с одинаковыми owner `gocream`, repository `pycdek` и environment `pypi`:

- `prerelease.yml` для beta и RC;
- `release.yml` для stable.

Если проекта `gocream-pycdek` ещё нет в PyPI, сначала создайте pending publisher для workflow, который выполнит первую публикацию. После первого выпуска добавьте второй publisher в настройках созданного проекта.

Для stable-релиза установите в репозиторий отдельный GitHub App с разрешением `Contents: Read and write`. Добавьте App в bypass list ruleset ветки `master` с режимом `Always allow`, чтобы только release-автоматизация могла отправить version/changelog commit напрямую в защищённую ветку. В настройках репозитория сохраните:

- App ID как Actions variable `RELEASE_APP_ID`;
- private key как Actions secret `RELEASE_APP_PRIVATE_KEY`.

Workflow создаёт временный installation token непосредственно перед checkout и передаёт его в Python Semantic Release. После завершения job токен автоматически отзывается.


## Beta Release

Beta выпускается вручную из выбранной рабочей ветки до её merge в `next`.

1. Переключитесь на commit, который нужно опубликовать, и проверьте ожидаемую версию:

	```sh
	git fetch --tags origin
	hatch run release:beta-preview
	```

2. Отправьте рабочую ветку в GitHub:

	```sh
	git push -u origin HEAD
	```

3. Откройте **Actions → Prerelease → Run workflow**.
4. В поле branch выберите отправленную рабочую ветку.
5. Запустите workflow и дождитесь его завершения.

Тот же запуск можно выполнить с локальной машины через GitHub CLI:

```sh
gh workflow run prerelease.yml --ref "$(git branch --show-current)"
```

Workflow создаст beta-тег на выбранном коммите, опубликует `sdist` и `wheel` в PyPI и создаст GitHub prerelease. Автоматические тесты перед ручной beta не запускаются, а дополнительный commit в рабочей ветке не появляется.

После проверки beta отправьте изменения pull request в `next`. Merge или push в `next` автоматически выпустит RC, если коммиты требуют изменения версии.

При выпуске beta из нескольких разошедшихся веток сначала синхронизируйте их с уже опубликованным beta-тегом, иначе PSR может предложить занятый номер и workflow остановится на проверке дубликата.


## Release Candidate

Каждый push или merge в `next` запускает workflow **Prerelease**, который сначала выполняет тесты на всех поддерживаемых версиях Python. После их успешного завершения параллельно запускаются выпуск RC и публикация документации `next`. Если коммиты содержат изменение версии, первый переход после beta будет выглядеть так:

```text
2.0.0-b.10 → 2.0.0-rc.1 → 2.0.0-rc.2
```

RC публикуется в PyPI и как GitHub prerelease. Версия и changelog не коммитятся в `next`. Если коммиты не требуют изменения версии, публикации не будет.

Сборка документации и выпуск RC используют один проверенный commit из `next`, но после тестов выполняются независимо: отсутствие новой версии не мешает обновить документацию, а ошибка одного направления не отменяет уже начавшееся второе.


## Stable Release

Stable-релиз запускается после merge любого pull request в `master`. Beta и RC перед ним необязательны: если prerelease существует, workflow финализирует его базовую версию; иначе следующая stable-версия вычисляется непосредственно по emoji-маркерам коммитов. Если релизных изменений нет, публикации не будет.

1. При необходимости предварительно выпустите и проверьте beta или RC в реальном проекте или приложении.
2. Создайте pull request в `master`.
3. Дождитесь успешного CI и review.
4. Выполните merge в `master`.
5. Дождитесь workflow **Release**: он повторно проверит commit в `master`, а затем выполнит релиз.
6. Создайте pull request из `master` обратно в `next`.

Workflow **Release** сначала вызывает общий набор проверок из `ci.yml`: матрицу тестов и контрольную сборку пакета. Только после их успеха Python Semantic Release вычисляет stable-версию, обновляет версию и `CHANGELOG.md`, создаёт release-коммит и stable-тег и отправляет их в `master`.

После сборки одного комплекта `sdist` и `wheel` независимо запускаются публикация в PyPI, создание GitHub Release и публикация документации. Ошибка одного направления не блокирует остальные, а весь workflow остаётся неуспешным, пока проблема не исправлена. Если проверки stable-кандидата не прошли, release-коммит, тег и публикации не создаются.

Обратная синхронизация `master` → `next` обязательна: стабильный release-коммит и тег должны находиться в истории дальнейшей разработки.


## Release Verification

После публикации проверьте:

- версию пакета в PyPI;
- успешные тесты и сборку stable-кандидата в workflow **Release**;
- тег и release или prerelease в GitHub;
- наличие одинаковых `sdist` и `wheel` в PyPI и GitHub;
- для stable - алиас документации `latest` и доступность старых версий.


## Release Artifacts

Для beta и RC workflow вычисляет версию, обновляет `__version__` и `CHANGELOG.md` во временном рабочем дереве и собирает из него пакет. Эти изменения попадают в `sdist` и `wheel`, но не коммитятся в исходную ветку; тег указывает на выбранный commit разработчика.

Подготовка metadata и сборка выполняются в одном job, поэтому между jobs передаются только готовые `sdist` и `wheel`.

Поэтому автоматически созданный GitHub-архив **Source code** для prerelease содержит исходную версию файлов. Официальные артефакты - приложенные `sdist` и `wheel`, в которых уже записаны правильные версия и changelog.

Для stable workflow **Release** сначала проверяет commit, попавший в `master`. После этого Python Semantic Release коммитит только версию и changelog, создаёт на этом release-коммите тег и запускает финальную сборку. Команда `hatch build --clean` очищает `dist/`, чтобы к новому релизу не примешались файлы предыдущей версии.


## Documentation

Документация публикуется через Mike:

- каждый успешный после тестов push в `next` обновляет документацию с алиасом `next`;
- stable-релиз публикует версию `major.minor` и переводит на неё алиас `latest`;
- ранее опубликованные версии сохраняются;
- опубликованный сайт и внешние ссылки при необходимости проверяются вручную.

Локальные команды:

```sh
hatch run docs:build
hatch run docs:links
hatch run docs:serve
hatch run docs:versions
hatch run docs:serve-versions
hatch run docs:links-external
```

Строгая сборка документации и проверка внутренних ссылок выполняются в CI для pull request в `master`. Workflow **Documentation** используется только для публикации версий `next` и `stable`.


## Troubleshooting

| Symptom | What to check |
|---|---|
| Релиз не создан | Emoji-маркеры после последнего тега и результат `hatch run release:preview` |
| Beta рассчитана неверно | Наличие канонического тега `2.0.0-b.9` |
| Публикация ожидает подтверждения | Required reviewer у environment `pypi` |
| PyPI отклоняет публикацию | Поля Trusted Publisher и environment `pypi` |
| Workflow не может создать тег или commit | Установка GitHub App, его `Contents` permission, bypass ruleset, `RELEASE_APP_ID` и `RELEASE_APP_PRIVATE_KEY` |
| Новый stable сообщает о незавершённом релизе | Наличие GitHub Release предыдущей версии; при его отсутствии повторный запуск упавших publication jobs |
| `docs:links-external` возвращает 404 | Выполнен ли первый deploy сайта; локальные ссылки проверяет `docs:links` |

Для ручной beta используйте `hatch run release:beta-preview`; для RC и stable - `hatch run release:preview`. Обе команды только показывают ожидаемую версию и не изменяют репозиторий.


## Versioning

Проект следует [Semantic Versioning][semver]. Уровень версии определяется по emoji-маркерам сообщений коммитов:

- `💥` повышает major;
- `✨` повышает minor;
- исправления, документация и другие поддерживаемые изменения повышают patch;
- коммиты без поддерживаемого маркера не создают релиз.

Полный список маркеров находится в секции `[tool.semantic_release.commit_parser_options]` файла `pyproject.toml`.

Git-теги используют SemVer-формат (`2.0.0-b.10`, `2.0.0-rc.1`). В метаданных Python те же версии нормализуются по PEP 440 (`2.0.0b10`, `2.0.0rc1`).


[semver]: https://semver.org/lang/ru/
