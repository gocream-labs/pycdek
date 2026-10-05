# Changelog

Все заметные изменения проекта документируются в этом файле. Версии следуют [Semantic Versioning](https://semver.org/lang/ru/).

<!--
	Файл ведёт python-semantic-release: при выпуске он вставляет новый раздел сразу под маркером ниже. Маркер не удалять - без него обновление молча не произойдёт. Формат разделов и правила ручной правки - в docs/releasing.md.
-->

<!-- version list -->

## v2.0.0 (2026-10-05)

### Refactoring

- ♻️ **client**: Refactor auth methods
  ([`af857d4`](https://github.com/gocream-labs/pycdek/commit/af857d4b7ce33cddc8907fed909a933d535cdb67))

- ♻️ **client**: Refactor authorization mechanics
  ([`e04696d`](https://github.com/gocream-labs/pycdek/commit/e04696d848c9891c6724b8682d29777b4b039f0d))

- ♻️ **client**: Refactor calculation
  ([`0afde40`](https://github.com/gocream-labs/pycdek/commit/0afde408a11572dfc23c0d6cb66f038f3cff3722))

- ♻️ **client**: Refactor delivery poinets method
  ([`43b942e`](https://github.com/gocream-labs/pycdek/commit/43b942e7ccf460a63ff0309115259f1cf8667a40))

- ♻️ **client**: Refactor get_order & remove_order methods
  ([`e191dad`](https://github.com/gocream-labs/pycdek/commit/e191dad0ea78ebc3c1f6f3e5e410010d918ab088))

- ♻️ **client**: Refactor intakes methods
  ([`4f119ac`](https://github.com/gocream-labs/pycdek/commit/4f119ac6e64c9034074fbdffa1274a6584bb7e2d))

- ♻️ **client**: Refactor location methods
  ([`1d43dec`](https://github.com/gocream-labs/pycdek/commit/1d43decff7041b7533aaf83214b89fb6b8a7847c))

- ♻️ **client**: Refactor receipt, barcode and download methods
  ([`525aae2`](https://github.com/gocream-labs/pycdek/commit/525aae2fbef8ace64775be372349167d5ae75c65))

- ♻️ **client**: Refactor registrate_order method
  ([`1cda502`](https://github.com/gocream-labs/pycdek/commit/1cda5022cb3931705e0d314950a71fef9d44b88f))

- ♻️ **client**: Refactor send method and docs
  ([`9919e7d`](https://github.com/gocream-labs/pycdek/commit/9919e7d856589181e821bcea1e0ca5d879adce8b))

- ♻️ **client**: Refactor webhook methods
  ([`4b4d427`](https://github.com/gocream-labs/pycdek/commit/4b4d427a4a20ca03515b607c6aa24dd254f0a78c))

### Tests

- 🧪 **client**: Add and update tests, and check with a api.edu.cdek.ru
  ([`7daeea0`](https://github.com/gocream-labs/pycdek/commit/7daeea0e99a41bad6d581832f8cbefe24e61df9e))

### Documentation

- 📝 **chore**: Update docs and comments
  ([`1078495`](https://github.com/gocream-labs/pycdek/commit/1078495fc11105ec0ad14b5a28b8f4698fa54a9c))

- 📝 **docs**: Update coverage API methods
  ([`ec631c8`](https://github.com/gocream-labs/pycdek/commit/ec631c82eab8c012da116230632b7211268c34b9))

- 📝 **docs**: Update docs and deprecation messages
  ([`5774783`](https://github.com/gocream-labs/pycdek/commit/5774783b23a30f163103514a157931def81688eb))

### Build System

- 🔧 **constants**: Add new statuses, tarrifs, services and overships
  ([`df33cc9`](https://github.com/gocream-labs/pycdek/commit/df33cc9db30d1d7ebf48198fcd6fffbe2177173c))

- 🏗️ **docs**: Remove release badge
  ([`17d326b`](https://github.com/gocream-labs/pycdek/commit/17d326b5ce8829b40e12da750051803c9d9b9903))

- 🔧 **docs**: Set up Google-style docstrings
  ([`08085aa`](https://github.com/gocream-labs/pycdek/commit/08085aafa0173453685b606f664896de31bdd3b3))

- 🔧 **project**: Change line length
  ([`e277340`](https://github.com/gocream-labs/pycdek/commit/e277340fa5c7c5aebb477cfcb9c589905d9ea43d))

- 🔧 **project**: Change titles for lint commits
  ([`4827014`](https://github.com/gocream-labs/pycdek/commit/48270143b36384ff189e3cdf63e3a996946f5f4a))

### Other

- 🧑‍💻 (chore): Add annotations
  ([`8ff1f3d`](https://github.com/gocream-labs/pycdek/commit/8ff1f3d134a260a97a677bd6813142f01124268c))

- 🧑‍💻 (chore): Add py.typed
  ([`82d5089`](https://github.com/gocream-labs/pycdek/commit/82d5089e1a70883900443d87fcb956fad70103a9))


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
