#
# created:   2022/04/20

# Order statuses
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-1.-Statusy-zakazov

ORDER_ACCEPTED = "ACCEPTED"  # Принят
# Заказ создан в информационной системе СДЭК, но требуются дополнительные валидации

ORDER_CREATED = "CREATED"  # Создан
# Заказ зарегистрирован в базе данных СДЭК

ORDER_REMOVED = "REMOVED"  # Удален
# Заказ отменен ИМ после регистрации в системе до прихода груза на склад СДЭК в городе-отправителе

ORDER_RECEIVED_AT_SHIPMENT_WAREHOUSE = "RECEIVED_AT_SHIPMENT_WAREHOUSE"  # Принят на склад отправителя
# Оформлен приход на склад СДЭК в городе-отправителе

ORDER_DELIVERED = "DELIVERED"  # Вручен
# Успешно доставлен и вручен адресату (конечный статус)

ORDER_NOT_DELIVERED = "NOT_DELIVERED"  # Не вручен
# Покупатель отказался от покупки, возврат в ИМ (конечный статус)

ORDER_READY_FOR_SHIPMENT_IN_SENDER_CITY = "READY_FOR_SHIPMENT_IN_SENDER_CITY"  # Готов к отправке в городе-отправителе
# Оформлен расход со склада СДЭК в городе отправителя. Груз подготовлен к отправке (консолидирован с другими заказами)

ORDER_TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY = (
    "TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY"  # Сдан перевозчику в городе-отправителе
)
# Зарегистрирована отправка в городе отправителе. Консолидированный груз передан на доставку (в аэропорт/загружен
# машину)

ORDER_SENT_TO_RECIPIENT_CITY = "SENT_TO_RECIPIENT_CITY"  # Отправлен в город-получатель
# Зарегистрирована отправка в город получателя, заказ в пути

ORDER_ACCEPTED_IN_RECIPIENT_CITY = "ACCEPTED_IN_RECIPIENT_CITY"  # Встречен в городе-получателе
# Зарегистрирована встреча заказа в городе получателя

ORDER_ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE = "ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE"  # Принят на склад доставки
# Оформлен приход на склад города-получателя, ожидает доставки до двери

ORDER_TAKEN_BY_COURIER = "TAKEN_BY_COURIER"  # Выдан на доставку
# Добавлен в курьерскую карту, выдан курьеру на доставку

ORDER_ACCEPTED_AT_PICK_UP_POINT = "ACCEPTED_AT_PICK_UP_POINT"  # Принят на склад до востребования
# Оформлен приход на склад города-получателя. Доставка до склада, посылка ожидает забора клиентом - покупателем ИМ

ORDER_ACCEPTED_AT_TRANSIT_WAREHOUSE = "ACCEPTED_AT_TRANSIT_WAREHOUSE"  # Принят на склад транзита
# Оформлен приход в городе-транзите

ORDER_RETURNED_TO_SENDER_CITY_WAREHOUSE = "RETURNED_TO_SENDER_CITY_WAREHOUSE"  # Возвращен на склад отправителя
# Повторно оформлен приход в городе-отправителе (не удалось передать перевозчику по какой-либо причине). Примечание:
# этот статус не означает возврат груза отправителю.

ORDER_RETURNED_TO_TRANSIT_WAREHOUSE = "RETURNED_TO_TRANSIT_WAREHOUSE"  # Возвращен на склад транзита
# Повторно оформлен приход в городе-транзите (груз возвращен на склад). Примечание: этот статус не означает возврат
# груза отправителю.

ORDER_RETURNED_TO_RECIPIENT_CITY_WAREHOUSE = "RETURNED_TO_RECIPIENT_CITY_WAREHOUSE"  # Возвращен на склад доставки
# Оформлен повторный приход на склад в городе-получателе. Доставка не удалась по какой-либо причине, ожидается
# очередная попытка доставки. Примечание: этот статус не означает возврат груза отправителю

ORDER_READY_FOR_SHIPMENT_IN_TRANSIT_CITY = "READY_FOR_SHIPMENT_IN_TRANSIT_CITY"  # Выдан на отправку в городе-транзите
# Оформлен расход в городе-транзите

ORDER_TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY = (
    "TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY"  # Сдан перевозчику в городе-транзите
)
# Зарегистрирована отправка у перевозчика в городе-транзите

ORDER_SENT_TO_TRANSIT_CITY = "SENT_TO_TRANSIT_CITY"  # Отправлен в город-транзит
# Зарегистрирована отправка в город-транзит. Проставлены дата и время отправления у перевозчика

ORDER_ACCEPTED_IN_TRANSIT_CITY = "ACCEPTED_IN_TRANSIT_CITY"  # Встречен в городе-транзите
# Зарегистрирована встреча в городе-транзите

ORDER_SENT_TO_SENDER_CITY = "SENT_TO_SENDER_CITY"  # Отправлен в город-отправитель
# Зарегистрирована отправка в город-отправитель, груз в пути

ORDER_ACCEPTED_IN_SENDER_CITY = "ACCEPTED_IN_SENDER_CITY"  # Встречен в городе-отправителе
# Зарегистрирована встреча груза в городе-отправителе

ORDER_ENTERED_TO_TRANSIT_WAREHOUSE = "ENTERED_TO_TRANSIT_WAREHOUSE"  # Поступил в город транзита
# Оформлена приемка в городе-транзите

ORDER_ENTERED_TO_RECIPIENT_CITY_WAREHOUSE = "ENTERED_TO_RECIPIENT_CITY_WAREHOUSE"  # Поступил на склад доставки
# Оформлена приемка на складе города получателя по заказу до двери

ORDER_ENTERED_TO_PICK_UP_POINT = "ENTERED_TO_PICK_UP_POINT"  # Поступил на склад до востребования
# Оформлена приемка на складе города получателя по заказу до склада

ORDER_IN_CUSTOMS_INTERNATIONAL = "IN_CUSTOMS_INTERNATIONAL"  # Таможенное оформление в стране отправления
# В процессе таможенного оформления в стране отправителя (для международных заказов)

ORDER_SHIPPED_TO_DESTINATION = "SHIPPED_TO_DESTINATION"  # Отправлено в страну назначения
# Отправлен в страну назначения, заказ в пути (для международных заказов)

ORDER_PASSED_TO_TRANSIT_CARRIER = "PASSED_TO_TRANSIT_CARRIER"  # Передано транзитному перевозчику
# Передано транзитному перевозчику

ORDER_IN_CUSTOMS_LOCAL = "IN_CUSTOMS_LOCAL"  # Таможенное оформление в стране назначения
# Таможенное оформление в стране назначения

ORDER_CUSTOMS_COMPLETE = "CUSTOMS_COMPLETE"  # Таможенное оформление завершено
# Завершено таможенное оформление заказа (для международных заказов)

ORDER_POSTOMAT_POSTED = "POSTOMAT_POSTED"  # Заложен в постамат
# Заложен в постамат, заказ ожидает забора клиентом - покупателем ИМ

ORDER_POSTOMAT_SEIZED = "POSTOMAT_SEIZED"  # Изъят из постамата курьером
# Истек срок хранения заказа в постамате, возврат в ИМ

ORDER_POSTOMAT_RECEIVED = "POSTOMAT_RECEIVED"  # Изъят из постамата клиентом
# Успешно изъят из постамата клиентом - покупателем ИМ

ORDER_INVALID = "INVALID"  # Некорректный заказ
# Заказ содержит некорректные данные


# Webhook Order statuses
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-1.-Statusy-zakazov
#
# Числовой код статуса из поля `status_code` вебхука ORDER_STATUS. В спецификации это поле помечено устаревшим:
# сравнивайте строковый код из поля `code` с константами `ORDER_*`. Новых числовых кодов здесь не добавляется,
# а дополнительные статусы, появившиеся позже, все приходят с общим кодом 1000.

WEBHOOK_ORDER_CREATED = 1  # Создан
# Заказ зарегистрирован в базе данных СДЭК

WEBHOOK_ORDER_DELETED = 2  # Удален. В спецификации: `REMOVED`
# Заказ отменен ИМ после регистрации в системе до прихода груза на склад СДЭК в городе-отправителе

WEBHOOK_ORDER_RECEIVED_AT_SHIPMENT_WAREHOUSE = 3  # Принят на склад отправителя
# Оформлен приход на склад СДЭК в городе-отправителе

WEBHOOK_ORDER_READY_FOR_SHIPMENT_IN_SENDER_CITY = 6  # Готов к отправке в городе-отправителе
# Оформлен расход со склада СДЭК в городе отправителя. Груз подготовлен к отправке (консолидирован с другими заказами)

WEBHOOK_ORDER_RETURNED_TO_SENDER_CITY_WAREHOUSE = 16  # Возвращен на склад отправителя
# Повторно оформлен приход в городе-отправителе (не удалось передать перевозчику по какой-либо причине). Примечание:
# этот статус не означает возврат груза отправителю.

WEBHOOK_ORDER_TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY = 7  # Сдан перевозчику в городе-отправителе
# Зарегистрирована отправка в городе отправителе. Консолидированный груз передан на доставку (в аэропорт/загружен
# машину)

WEBHOOK_ORDER_SENT_TO_TRANSIT_CITY = 21  # Отправлен в город-транзит
# Зарегистрирована отправка в город-транзит. Проставлены дата и время отправления у перевозчика

WEBHOOK_ORDER_ACCEPTED_IN_TRANSIT_CITY = 22  # Встречен в городе-транзите
# Зарегистрирована встреча в городе-транзите

WEBHOOK_ORDER_ACCEPTED_AT_TRANSIT_WAREHOUSE = 13  # Принят на склад транзита
# Оформлен приход в городе-транзите

WEBHOOK_ORDER_RETURNED_TO_TRANSIT_WAREHOUSE = 17  # Возвращен на склад транзита
# Повторно оформлен приход в городе-транзите (груз возвращен на склад). Примечание: этот статус не означает возврат
# груза отправителю.

WEBHOOK_ORDER_READY_FOR_SHIPMENT_IN_TRANSIT_CITY = 19  # Выдан на отправку в городе-транзите
# Оформлен расход в городе-транзите

WEBHOOK_ORDER_TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY = 20  # Сдан перевозчику в городе-транзите
# Зарегистрирована отправка у перевозчика в городе-транзите

WEBHOOK_ORDER_SENT_TO_SENDER_CITY = 27  # Отправлен в город-отправитель
# Зарегистрирована отправка в город-отправитель, груз в пути

WEBHOOK_ORDER_SENT_TO_RECIPIENT_CITY = 8  # Отправлен в город-получатель
# Зарегистрирована отправка в город получателя, заказ в пути

WEBHOOK_ORDER_ACCEPTED_IN_SENDER_CITY = 28  # Встречен в городе-отправителе
# Зарегистрирована встреча груза в городе-отправителе

WEBHOOK_ORDER_ACCEPTED_IN_RECIPIENT_CITY = 9  # Встречен в городе-получателе
# Зарегистрирована встреча заказа в городе получателя

WEBHOOK_ORDER_ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE = 10  # Принят на склад доставки
# Оформлен приход на склад города-получателя, ожидает доставки до двери

WEBHOOK_ORDER_ACCEPTED_AT_PICK_UP_POINT = 12  # Принят на склад до востребования
# Оформлен приход на склад города-получателя. Доставка до склада, посылка ожидает забора клиентом - покупателем ИМ

WEBHOOK_ORDER_TAKEN_BY_COURIER = 11  # Выдан на доставку
# Добавлен в курьерскую карту, выдан курьеру на доставку

WEBHOOK_ORDER_RETURNED_TO_RECIPIENT_CITY_WAREHOUSE = 18  # Возвращен на склад доставки
# Оформлен повторный приход на склад в городе-получателе. Доставка не удалась по какой-либо причине, ожидается
# очередная попытка доставки. Примечание: этот статус не означает возврат груза отправителю

WEBHOOK_ORDER_DELIVERED = 4  # Вручен
# Успешно доставлен и вручен адресату (конечный статус)

WEBHOOK_ORDER_NOT_DELIVERED = 5  # Не вручен
# Покупатель отказался от покупки, возврат в ИМ (конечный статус)


# Document statuses

# квитанции | receipt
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-10.-Statusy-kvitancii

# ШК места | Barcode CP
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-11.-Statusy-ShK-mesta

DOCUMENT_ACCEPTED = "ACCEPTED"  # Принят | Запрос на формирование квитанции / ШК места принят
DOCUMENT_PROCESSING = "PROCESSING"  # Формируется | Файл с квитанцией / ШК места формируется
DOCUMENT_READY = "READY"  # Сформирован | Файл с квитанцией / ШК места и ссылка на скачивание файла сформированы
DOCUMENT_REMOVED = "REMOVED"  # Удален | Истекло время жизни ссылки на скачивание файла с квитанцией / ШК места
DOCUMENT_INVALID = "INVALID"  # Некорректный запрос | Некорректный запрос на формирование квитанции / ШК места
