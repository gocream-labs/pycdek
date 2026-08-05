# Changelog

Все заметные изменения проекта документируются в этом файле. Версии следуют [Semantic Versioning](https://semver.org/lang/ru/).

<!--
	Файл ведёт python-semantic-release: при выпуске он вставляет новый раздел сразу под маркером ниже. Маркер не удалять - без него обновление молча не произойдёт. Формат разделов и правила ручной правки - в docs/releasing.md.
-->

<!-- version list -->

## v2.0.0-rc.1 (2026-08-04)

### Breaking Changes

- 💥 **release**: Commit to break version for PSR
	([`9816b1c`](https://github.com/gocream-labs/pycdek/commit/9816b1cba73cc44fab91b0a4cd4a56964cd4ce33))

### Licensing

- 📄 **project**: Change license GPLv3 -> MPL-2.0
	([`9521005`](https://github.com/gocream-labs/pycdek/commit/952100544c5c83d99867cddc429b2232471af1c2))

### Refactoring

- 🎨 **git**: Ignore formatting commit in blame
	([`04d14e1`](https://github.com/gocream-labs/pycdek/commit/04d14e1461a869b8c4b23fd73a65b56647507c50))

- 🎨 **poject**: Update lint config and code style
	([`3fa42b6`](https://github.com/gocream-labs/pycdek/commit/3fa42b69e8deb15c41bd42982baf2bd407fc3826))

- ⚰️ **project**: Remove unnecessary comments
	([`e94f8b8`](https://github.com/gocream-labs/pycdek/commit/e94f8b8c591bbed0a6a287ea2be949cb8169f9e8))

- 🎨 **style**: Format code with Ruff
	([`3eb1d31`](https://github.com/gocream-labs/pycdek/commit/3eb1d31f81c5d9ec70a4a0b0db783a70fb9cda70))

### Tests

- 🧪 **tests**: Add tests
	([`48d7ee3`](https://github.com/gocream-labs/pycdek/commit/48d7ee3a551bbc474e1f0acaa04c7b0d397c5ccc),[`c4be238`](https://github.com/gocream-labs/pycdek/commit/c4be23835a875e4cefd79addc0e2b3aa033658fd))

### Documentation

- 📝 **docs**: Add mkdocs
	([`54d00e6`](https://github.com/gocream-labs/pycdek/commit/54d00e6af4df97cc97151e923b7fecfccd9c2b27))

- 📝 **docs**: Big update docs
	([`16342fe`](https://github.com/gocream-labs/pycdek/commit/16342fe5ef0a35c6343153bafd5dec0a346a225b))

- 📝 **docs**: Update api links
	([`974dea9`](https://github.com/gocream-labs/pycdek/commit/974dea91642de0b55774ac724b3555096206d7e6))

- 📝 **docs**: Update Contributing
	([`52a77bf`](https://github.com/gocream-labs/pycdek/commit/52a77bf9532aec81b4d688988638456a7fd29dcb))

- 📝 **readme**: Back to work
	([`a18bade`](https://github.com/gocream-labs/pycdek/commit/a18bade40a60fa159d4c4fb1718e2d02917f1e52))

### Build System

- 🧱 **project**: Add lint commit script
	([`f5f8c87`](https://github.com/gocream-labs/pycdek/commit/f5f8c874a7e1bc4560310f314c56d16fb9bddb6c))

- 🏗️ **project**: Big reconfigure of project
	([`763fb20`](https://github.com/gocream-labs/pycdek/commit/763fb207abf91ab4b10516700ee2a18b23295c8c))

- 🏗️ **project**: Configure lints
	([`3f94d16`](https://github.com/gocream-labs/pycdek/commit/3f94d163b32d085d3fc155ff49d06d8fea121f9c))

- 🏗️ **project**: Rename for deploy on PyPI
	([`3596e8f`](https://github.com/gocream-labs/pycdek/commit/3596e8fafcc2cf65913ad94202c288dcfea2f98c))

- 🏗️ **project**: Update authors
	([`f4f492d`](https://github.com/gocream-labs/pycdek/commit/f4f492d4cb7da384c565e40419962a32ad73ebf4))

- 🏗️ **project**: Update gitignore
	([`21506e2`](https://github.com/gocream-labs/pycdek/commit/21506e26ced561d9e0d34922d68278d7348e5282))

- 🏗️ **project**: Update python versions
	([`34bf61c`](https://github.com/gocream-labs/pycdek/commit/34bf61c99b24c22996a41ad136d943d08a8cd685))

- 🏗️ **release**: Bootstrap release workflows
	([`ea8bf0a`](https://github.com/gocream-labs/pycdek/commit/ea8bf0a261864a63ac99ad74020797774443741d), [`1ca90d5`](https://github.com/gocream-labs/pycdek/commit/1ca90d57adfc8f25b1955965b0b22c99ca32517c))

### Other

- Update statuses
	([`f51d494`](https://github.com/gocream-labs/pycdek/commit/f51d49431dea22e7bd4b42fb06ab9e2f18501f6c))


## v2.0.0-b.9 (2022-04-18)

_Эта и более ранние версии восстановлены в сокращённом виде: коммиты того времени не соответствуют текущему gitmoji-формату и не могут быть надёжно разобраны генератором._

### Features

- Поддержка дополнительных статусов заказов СДЭК
	([`fcf9393`](https://github.com/gocream-labs/pycdek/commit/fcf93933e7c5b306c39b1160ddfdb8530089cf32))

- Ошибка `ERR_INVALID_TARIFF_WITH_DATETIMEORDERSEND` для устаревшего калькулятора
	([`f5e6c06`](https://github.com/gocream-labs/pycdek/commit/f5e6c06d47a3a2dab53645d91e953b31865b9e98))

### Documentation

- Обновлены ссылки на документацию API СДЭК
	([`3566220`](https://github.com/gocream-labs/pycdek/commit/3566220cc3346b7c771e49c129467d1d2c8ff51e))
