# Known Issues

Эти проблемы известны и будут последовательно исправляться до выхода стабильной версии 2.0.0.

| Где | Проблема |
|---|---|
| `authorization` | Учётные данные передаются в query-параметрах POST-запроса. Перенос в тело формы отложен до подтверждения поддержки со стороны СДЭК. |
| [`client.py:251`][client-251] | Сборка URL через `pathlib.Path` ломается на Windows. |
| [`client.py:671`][client-671] | `remove_intakes` возвращает `Response`, а не `dict`. |
| [`client.py:76`][client-76] / [`statuses.py:15`][statuses-15] | Для одного статуса используются разные значения: `RECEIVED_AT_SENDER_WAREHOUSE` и `RECEIVED_AT_SHIPMENT_WAREHOUSE`. |
| [`client.py:83`][client-83] / [`statuses.py:56`][statuses-56] | Для одного статуса используются разные значения: `ARRIVED_AT_RECIPIENT_CITY` и `ACCEPTED_IN_RECIPIENT_CITY`. |
| [`client.py:997`][client-997] | `get_shipping_cost` использует снятый с поддержки калькулятор v1.5. |
| [`utils.py:10`][utils-10] | `clear_dict` не обрабатывает списки словарей. Исправляться не будет: функция объявлена устаревшей в пользу `drop_none` и удаляется в 3.0.0. Методы клиента переводятся на неё по мере переработки. |

[client-251]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/client.py#L251
[client-671]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/client.py#L671
[client-76]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/client.py#L76
[statuses-15]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/statuses.py#L15
[client-83]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/client.py#L83
[statuses-56]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/statuses.py#L56
[client-997]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/client.py#L997
[utils-10]: https://github.com/gocream-labs/pycdek/blob/master/gocream_pycdek/utils.py#L10
