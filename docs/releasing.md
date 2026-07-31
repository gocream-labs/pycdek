# Releasing and Versioning

Версионирование следует [SemVer][semver]. Версия хранится литералом в
`pycdek/__init__.py`: её читает Hatchling, а при релизе изменяет
`python-semantic-release`.

Следующая версия определяется по gitmoji в коммитах после прошлого тега:
`💥` повышает major, `✨` — minor, остальные поддерживаемые изменения — patch.
Перед стабильным релизом выпускается `rc`-версия.

Проверка результата без записи:

```sh
hatch run release:preview
```

При необходимости уровень изменения задаётся явно:

```sh
semantic-release version --major
semantic-release version --major --as-prerelease
semantic-release version --minor
```

## First 2.0.0 Release

PSR не считает бету `2.0.0b9` последним стабильным тегом. Для выпуска именно
`2.0.0` нужен флаг `--major`.

Версия в `pycdek/__init__.py` записана как `2.0.0-b.9`, чтобы PSR корректно
разбирал её как SemVer-пререлиз. При установке PEP 440 нормализует её обратно в
`2.0.0b9`; единственное отличие — значение `pycdek.__version__` в рантайме.

Историю до 2.0.0 нужно добавить в `CHANGELOG.md` вручную: старые коммиты не
соответствуют формату gitmoji.

[semver]: https://semver.org/lang/ru/
