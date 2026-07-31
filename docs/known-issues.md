# Known Issues

Эти проблемы известны и намеренно сохраняются в 2.0.0 ради совместимости.
Исправления, меняющие наблюдаемое поведение, запланированы для 3.0.0.

| Где | Проблема |
|---|---|
| [`client.py:219`](../pycdek/client.py#L219) | Разбор ошибки авторизации проверяет наличие `invalid_client` вместо значения `error`; ветка `CdekApiAccessException` недостижима. |
| [`client.py:206`](../pycdek/client.py#L206) | Учётные данные передаются в query string. |
| [`client.py:489`](../pycdek/client.py#L489) | `get_order` не пробрасывает `raise_errors` в `send()`. |
| [`client.py:251`](../pycdek/client.py#L251) | Сборка URL через `pathlib.Path` ломается на Windows. |
| [`client.py:281`](../pycdek/client.py#L281) | `send()` падает с `UnboundLocalError` на неподдерживаемом HTTP-методе. |
| [`client.py:529`](../pycdek/client.py#L529), [`client.py:671`](../pycdek/client.py#L671) | `remove_order` и `remove_intakes` возвращают `Response`, а не `dict`. |
| [`client.py:76`](../pycdek/client.py#L76) / [`statuses.py:15`](../pycdek/statuses.py#L15) | Для одного статуса используются разные значения: `RECEIVED_AT_SENDER_WAREHOUSE` и `RECEIVED_AT_SHIPMENT_WAREHOUSE`. |
| [`client.py:83`](../pycdek/client.py#L83) / [`statuses.py:56`](../pycdek/statuses.py#L56) | Для одного статуса используются разные значения: `ARRIVED_AT_RECIPIENT_CITY` и `ACCEPTED_IN_RECIPIENT_CITY`. |
| [`client.py:997`](../pycdek/client.py#L997) | `get_shipping_cost` использует снятый с поддержки калькулятор v1.5. |
| [`client.py:1299`](../pycdek/client.py#L1299) | `get_deliverypoints` отправляет имена параметров из API v1. |
| [`utils.py:10`](../pycdek/utils.py#L10) | `clear_dict` не обрабатывает списки словарей. |
| [`exceptions.py:71`](../pycdek/exceptions.py#L71) | `CdekRequestException` объявлен, но нигде не используется. |
