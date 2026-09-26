# Покрытие API

Соответствие эндпоинтов API v2 методам клиента. Список эндпоинтов сверен 26 сентября 2026 года с [официальной OpenAPI-спецификацией СДЭК](https://gateway.cdek.ru/api-cdek-docs/web/docs/merged?sectionId=api_v2_integration).

Покрыто 22 из 48 эндпоинтов. Остальные можно вызвать через [`send`][gocream_pycdek.client.CdekClient.send]: метод добавит авторизацию и базовый URL, но тело запроса и разбор ответа остаются на вызывающей стороне.

```python
response = client.send("v2/calculator/tarifflist", method="post", data=payload)
```


## Авторизация

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `POST` | `/v2/oauth/token` | Получение токена авторизации | [`authorization`][gocream_pycdek.client.CdekClient.authorization] |


## Локации

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `GET` | `/v2/location/regions` | Получение списка регионов | [`get_regions`][gocream_pycdek.client.CdekClient.get_regions], [`get_all_regions`][gocream_pycdek.client.CdekClient.get_all_regions] |
| `GET` | `/v2/location/cities` | Получение списка населённых пунктов | [`get_cities`][gocream_pycdek.client.CdekClient.get_cities], [`get_all_cities`][gocream_pycdek.client.CdekClient.get_all_cities] |
| `GET` | `/v2/location/suggest/cities` | Подбор локации по названию города | — |
| `GET` | `/v2/location/postalcodes` | Получение почтовых индексов города | — |
| `GET` | `/v2/location/coordinates` | Получение локации по координатам | — |


## Офисы

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `GET` | `/v2/deliverypoints` | Получение списка офисов | [`get_deliverypoints`][gocream_pycdek.client.CdekClient.get_deliverypoints] |
| `GET` | `/v2/deliverypoints/byPolygons` | Получение списка офисов внутри прямоугольника координат | — |


## Калькулятор

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `POST` | `/v2/calculator/tariff` | Расчёт по коду тарифа | [`calculator_tariff`][gocream_pycdek.client.CdekClient.calculator_tariff] |
| `POST` | `/v2/calculator/tarifflist` | Расчёт по доступным тарифам | — |
| `POST` | `/v2/calculator/tariffAndService` | Расчёт по доступным тарифам и дополнительным услугам | — |
| `GET` | `/v2/calculator/alltariffs` | Список доступных тарифов | — |

Устаревший [`get_shipping_cost`][gocream_pycdek.client.CdekClient.get_shipping_cost] обращается к legacy-калькулятору `calculator/calculate_price_by_json.php`, которого нет в спецификации API v2.


## Заказы

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `POST` | `/v2/orders` | Регистрация заказа | [`registrate_order`][gocream_pycdek.client.CdekClient.registrate_order] |
| `GET` | `/v2/orders` | Получение информации о заказе по номеру СДЭК или ИМ | [`get_order`][gocream_pycdek.client.CdekClient.get_order] |
| `GET` | `/v2/orders/{uuid}` | Получение информации о заказе по UUID | [`get_order`][gocream_pycdek.client.CdekClient.get_order] |
| `DELETE` | `/v2/orders/{uuid}` | Удаление заказа | [`remove_order`][gocream_pycdek.client.CdekClient.remove_order] |
| `PATCH` | `/v2/orders` | Изменение заказа | — |
| `GET` | `/v2/orders/{orderUuid}/intakes` | Получение информации о всех заявках по заказу | — |
| `POST` | `/v2/orders/{uuid}/refusal` | Регистрация отказа | — |
| `POST` | `/v2/orders/{uuid}/clientReturn` | Регистрация клиентского возврата | — |


## Заявки на вызов курьера

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `POST` | `/v2/intakes` | Регистрация заявки на вызов курьера | [`registrate_intakes`][gocream_pycdek.client.CdekClient.registrate_intakes] |
| `GET` | `/v2/intakes/{uuid}` | Получение информации о заявке по UUID | [`get_intakes`][gocream_pycdek.client.CdekClient.get_intakes] |
| `DELETE` | `/v2/intakes/{uuid}` | Удаление заявки | [`remove_intakes`][gocream_pycdek.client.CdekClient.remove_intakes] |
| `PATCH` | `/v2/intakes` | Изменение статуса заявки на вызов курьера | — |
| `POST` | `/v2/intakes/availableDays` | Получение дат вызова курьера для населённого пункта | — |


## Печатные формы

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `POST` | `/v2/print/orders` | Формирование квитанции к заказу | [`request_receipt`][gocream_pycdek.client.CdekClient.request_receipt] |
| `GET` | `/v2/print/orders/{uuid}` | Получение квитанции к заказу | [`get_receipt`][gocream_pycdek.client.CdekClient.get_receipt] |
| `GET` | `/v2/print/orders/{uuid}.pdf` | Скачивание готовой квитанции | [`download`][gocream_pycdek.client.CdekClient.download] |
| `POST` | `/v2/print/barcodes` | Формирование ШК места к заказу | [`request_barcode`][gocream_pycdek.client.CdekClient.request_barcode] |
| `GET` | `/v2/print/barcodes/{uuid}` | Получение ШК места к заказу | [`get_barcode`][gocream_pycdek.client.CdekClient.get_barcode] |
| `GET` | `/v2/print/barcodes/{uuid}.pdf` | Скачивание готового ШК | [`download`][gocream_pycdek.client.CdekClient.download] |

`download` принимает готовую ссылку `url` из ответа `get_receipt` или `get_barcode`, а не UUID.


## Вебхуки

| Метод | Эндпоинт | Описание | Клиент |
|---|---|---|---|
| `POST` | `/v2/webhooks` | Добавление подписки на вебхуки | [`subscribe`][gocream_pycdek.client.CdekClient.subscribe] |
| `GET` | `/v2/webhooks` | Получение информации о подписках на вебхуки | [`subscribe_info`][gocream_pycdek.client.CdekClient.subscribe_info] |
| `GET` | `/v2/webhooks/{uuid}` | Получение информации о подписке по UUID | [`subscribe_info_by_uuid`][gocream_pycdek.client.CdekClient.subscribe_info_by_uuid] |
| `DELETE` | `/v2/webhooks/{uuid}` | Удаление подписки по UUID | [`subscribe_delete`][gocream_pycdek.client.CdekClient.subscribe_delete] |


## Не покрытые разделы

Для этих разделов API в клиенте нет ни одного метода.

| Метод | Эндпоинт | Описание |
|---|---|---|
| `GET` | `/v2/delivery/intervals` | Получение интервалов доставки |
| `POST` | `/v2/delivery/estimatedIntervals` | Получение интервалов доставки до создания заказа |
| `POST` | `/v2/delivery` | Регистрация договорённости о доставке |
| `GET` | `/v2/delivery/{uuid}` | Получение информации о договорённости о доставке |
| `POST` | `/v2/prealert` | Регистрация преалерта |
| `GET` | `/v2/prealert/{uuid}` | Получение информации о преалерте |
| `POST` | `/v2/photoDocument` | Получение заказов с готовыми фото |
| `GET` | `/v2/photoDocument/{uuid}` | Скачивание готового архива |
| `POST` | `/v2/reverse/availability` | Проверка доступности реверса |
| `POST` | `/v2/international/package/restrictions` | Получение ограничений по международным заказам |
| `GET` | `/v2/registries` | Получение информации о реестрах наложенного платежа |
| `GET` | `/v2/passport` | Получение информации о паспортных данных |
| `GET` | `/v2/check` | Получение информации о чеках |
