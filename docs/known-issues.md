# Known Issues

Ниже перечислены оставшиеся ограничения обработки ошибок и устаревших методов текущей реализации.


## Remaining Limitations

| Где | Ограничение и дальнейшее действие |
|---|---|
| [`get_all_regions`][gocream_pycdek.client.CdekClient.get_all_regions], [`get_all_cities`][gocream_pycdek.client.CdekClient.get_all_cities] | При `raise_errors=False` словарь ошибки может быть принят за страницу: генератор выдаёт его ключи и продолжает запросы. Используйте стандартное `raise_errors=True`; изменение обработки ошибок планируется отдельно. |
| Методы, извлекающие `entity` | При `raise_errors=False` ответ без `entity` приводит к `KeyError`. Для ручной обработки такого ответа используйте `origin_response=True`. Унификация ошибок отложена на 3.0.0. |
| [`get_shipping_cost`][gocream_pycdek.client.CdekClient.get_shipping_cost] | Legacy-калькулятор deprecated с 2.0.0, удаление запланировано в 3.0.0. Аргументы `auth_login` и `secure` не используются; при `auth=True` берутся credentials клиента. Без `auth=True` тестовый контур отвечает ошибкой `ERROR_REQUEST_AUTH_IS_EMPTY`. |
| [`get_regions`][gocream_pycdek.client.CdekClient.get_regions] (`region_code`, `kladr_region_code`), [`get_cities`][gocream_pycdek.client.CdekClient.get_cities] (`kladr_region_code`) | Отсутствуют в текущей спецификации API v2 для этих методов; поддержка не подтверждена. Deprecated с 2.0.0 (`DeprecationWarning`), удаление запланировано в 3.0.0. |
| [`get_regions`][gocream_pycdek.client.CdekClient.get_regions], [`get_cities`][gocream_pycdek.client.CdekClient.get_cities] (`fias_region_guid`) | Помечено устаревшим в спецификации API - значения могут быть неактуальны. Deprecated с 2.0.0 (`DeprecationWarning`); замены в спецификации не указано, снимать поддержку не планируется. |
| [`clear_dict`][gocream_pycdek.utils.clear_dict] | Не обрабатывает словари внутри списков; поведение зафиксировано ожидаемо падающим тестом. Исправляться не будет: функция и `is_empty` удаляются в 3.0.0. Единственный внутренний вызов остаётся в `get_shipping_cost`; актуальные методы используют `drop_none`. |
| [`remove_intakes`][gocream_pycdek.client.CdekClient.remove_intakes] | Возвращает исходный `Response`, а не `entity`, как соседние методы. Сохранено для совместимости второй версии; унификация возвращаемых значений запланирована в 3.0.0. |
| [`registrate_order`][gocream_pycdek.client.CdekClient.registrate_order] | Пустые строки и `null` во вложенных словарях передаются как есть ([`drop_none`][gocream_pycdek.utils.drop_none]). Регистрацию с ними тестовый контур принимает (202), но итог асинхронной валидации заказа не подтверждён: при проверке 26 сентября 2026 года контур не обработал ни одну регистрацию заказа. |
