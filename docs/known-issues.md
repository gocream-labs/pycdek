# Known Issues

Эти проблемы известны и намеренно сохраняются в 2.0.0 ради совместимости.
Исправления, меняющие наблюдаемое поведение, запланированы для 3.0.0.

| Где | Проблема |
|---|---|
| [`client.py:219`][client-219] | Разбор ошибки авторизации проверяет наличие `invalid_client` вместо значения `error`; ветка `CdekApiAccessException` недостижима. |
| [`client.py:206`][client-206] | Учётные данные передаются в query string. |
| [`client.py:489`][client-489] | `get_order` не пробрасывает `raise_errors` в `send()`. |
| [`client.py:251`][client-251] | Сборка URL через `pathlib.Path` ломается на Windows. |
| [`client.py:281`][client-281] | `send()` падает с `UnboundLocalError` на неподдерживаемом HTTP-методе. |
| [`client.py:529`][client-529], [`client.py:671`][client-671] | `remove_order` и `remove_intakes` возвращают `Response`, а не `dict`. |
| [`client.py:76`][client-76] / [`statuses.py:15`][statuses-15] | Для одного статуса используются разные значения: `RECEIVED_AT_SENDER_WAREHOUSE` и `RECEIVED_AT_SHIPMENT_WAREHOUSE`. |
| [`client.py:83`][client-83] / [`statuses.py:56`][statuses-56] | Для одного статуса используются разные значения: `ARRIVED_AT_RECIPIENT_CITY` и `ACCEPTED_IN_RECIPIENT_CITY`. |
| [`client.py:997`][client-997] | `get_shipping_cost` использует снятый с поддержки калькулятор v1.5. |
| [`client.py:1299`][client-1299] | `get_deliverypoints` отправляет имена параметров из API v1. |
| [`utils.py:10`][utils-10] | `clear_dict` не обрабатывает списки словарей. |
| [`exceptions.py:71`][exceptions-71] | `CdekRequestException` объявлен, но нигде не используется. |

[client-219]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L219
[client-206]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L206
[client-489]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L489
[client-251]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L251
[client-281]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L281
[client-529]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L529
[client-671]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L671
[client-76]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L76
[statuses-15]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/statuses.py#L15
[client-83]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L83
[statuses-56]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/statuses.py#L56
[client-997]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L997
[client-1299]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/client.py#L1299
[utils-10]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/utils.py#L10
[exceptions-71]: https://github.com/gocream/pycdek/blob/master/gocream_pycdek/exceptions.py#L71
