# -*- coding: utf-8 -*-
#
# created:   2022/04/20

# Order statuses
# ru: https://api-docs.cdek.ru/29923975.html - Приложение 1. Статусы заказов
# en: https://api-docs.cdek.ru/33828849.html - Appendix 1. Order Statuses

ORDER_ACCEPTED = "ACCEPTED"  # Принят
# Заказ создан в информационной системе СДЭК, но требуются дополнительные валидации

ORDER_CREATED = "CREATED"  # Создан
# Заказ создан в информационной системе СДЭК и прошел необходимые валидации

ORDER_RECEIVED_AT_SHIPMENT_WAREHOUSE = "RECEIVED_AT_SHIPMENT_WAREHOUSE"  # Принят на склад отправителя
# Оформлен приход на склад СДЭК в городе-отправителе.

ORDER_READY_FOR_SHIPMENT_IN_SENDER_CITY = "READY_FOR_SHIPMENT_IN_SENDER_CITY"  # Выдан на отправку в г. отправителе
# Оформлен расход со склада СДЭК в городе-отправителе. Груз подготовлен к отправке (консолидирован с другими посылками)

ORDER_RETURNED_TO_SENDER_CITY_WAREHOUSE = "RETURNED_TO_SENDER_CITY_WAREHOUSE"  # Возвращен на склад отправителя
# Повторно оформлен приход в городе-отправителе (не удалось передать перевозчику по какой-либо причине).
# Примечание: этот статус не означает возврат груза отправителю.

ORDER_TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY = (
    "TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY"  # Сдан перевозчику в г. отправителе
)
# Зарегистрирована отправка в городе-отправителе. Консолидированный груз передан на доставку (в аэропорт/загружен машину)

ORDER_SENT_TO_TRANSIT_CITY = "SENT_TO_TRANSIT_CITY"  # Отправлен в г. транзит
# Зарегистрирована отправка в город-транзит. Проставлены дата и время отправления у перевозчика

ORDER_ACCEPTED_IN_TRANSIT_CITY = "ACCEPTED_IN_TRANSIT_CITY"  # Встречен в г. транзите
# Зарегистрирована встреча в городе-транзите

ORDER_ACCEPTED_AT_TRANSIT_WAREHOUSE = "ACCEPTED_AT_TRANSIT_WAREHOUSE"  # Принят на склад транзита
# Оформлен приход в городе-транзите

ORDER_RETURNED_TO_TRANSIT_WAREHOUSE = "RETURNED_TO_TRANSIT_WAREHOUSE"  # Возвращен на склад транзита
# Повторно оформлен приход в городе-транзите (груз возвращен на склад).
# Примечание: этот статус не означает возврат груза отправителю.

ORDER_READY_FOR_SHIPMENT_IN_TRANSIT_CITY = "READY_FOR_SHIPMENT_IN_TRANSIT_CITY"  # Выдан на отправку в г. транзите
# Оформлен расход в городе-транзите

ORDER_TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY = (
    "TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY"  # Сдан перевозчику в г. транзите
)
# Зарегистрирована отправка у перевозчика в городе-транзите

ORDER_SENT_TO_SENDER_CITY = "SENT_TO_SENDER_CITY"  # Отправлен в г. отправитель
# Зарегистрирована отправка в город-отправитель, груз в пути

ORDER_SENT_TO_RECIPIENT_CITY = "SENT_TO_RECIPIENT_CITY"  # Отправлен в г. получатель
# Зарегистрирована отправка в город-получатель, груз в пути

ORDER_ACCEPTED_IN_SENDER_CITY = "ACCEPTED_IN_SENDER_CITY"  # Встречен в г. отправителе
# Зарегистрирована встреча груза в городе-отправителе

ORDER_ACCEPTED_IN_RECIPIENT_CITY = "ACCEPTED_IN_RECIPIENT_CITY"  # Встречен в г. получателе
# Зарегистрирована встреча груза в городе-получателе

ORDER_ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE = "ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE"  # Принят на склад доставки
# Оформлен приход на склад города-получателя, ожидает доставки до двери

ORDER_ACCEPTED_AT_PICK_UP_POINT = "ACCEPTED_AT_PICK_UP_POINT"  # Принят на склад до востребования
# Оформлен приход на склад города-получателя. Доставка до склада, посылка ожидает забора клиентом - покупателем ИМ

ORDER_TAKEN_BY_COURIER = "TAKEN_BY_COURIER"  # Выдан на доставку
# Добавлен в курьерскую карту, выдан курьеру на доставку

ORDER_RETURNED_TO_RECIPIENT_CITY_WAREHOUSE = "RETURNED_TO_RECIPIENT_CITY_WAREHOUSE"  # Возвращен на склад доставки
# Оформлен повторный приход на склад в городе-получателе. Доставка не удалась по какой-либо причине, ожидается очередная попытка доставки.
# Примечание: этот статус не означает возврат груза отправителю.

ORDER_DELIVERED = "DELIVERED"  # Вручен
# Успешно доставлен и вручен адресату (конечный статус).

ORDER_NOT_DELIVERED = "NOT_DELIVERED"  # Не вручен
# Покупатель отказался от покупки, возврат в ИМ (конечный статус).

ORDER_INVALID = "INVALID"  # Некорректный заказ
# Заказ содержит некорректные данные


# Webhook Order statuses
# ru: https://api-docs.cdek.ru/29924139.html - Приложение 1. Статусы заказов
# en: https://api-docs.cdek.ru/33828884.html - Appendix 1. Order Statuses

WEBHOOK_ORDER_CREATED = 1  # Создан
# Заказ зарегистрирован в базе данных СДЭК

WEBHOOK_ORDER_DELETED = 2  # Удален
# Заказ отменен ИМ после регистрации в системе до прихода груза на склад СДЭК в городе-отправителе

WEBHOOK_ORDER_RECEIVED_AT_SHIPMENT_WAREHOUSE = 3  # Принят на склад отправителя
# Оформлен приход на склад СДЭК в городе-отправителе.

WEBHOOK_ORDER_READY_FOR_SHIPMENT_IN_SENDER_CITY = 6  # Выдан на отправку в г. отправителе
# Оформлен расход со склада СДЭК в городе-отправителе. Груз подготовлен к отправке (консолидирован с другими посылками)

WEBHOOK_ORDER_RETURNED_TO_SENDER_CITY_WAREHOUSE = 16  # Возвращен на склад отправителя
# Повторно оформлен приход в городе-отправителе (не удалось передать перевозчику по какой-либо причине).
# Примечание: этот статус не означает возврат груза отправителю.

WEBHOOK_ORDER_TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY = 7  # Сдан перевозчику в г. отправителе
# Зарегистрирована отправка в городе-отправителе. Консолидированный груз передан на доставку (в аэропорт/загружен машину)

WEBHOOK_ORDER_SENT_TO_TRANSIT_CITY = 21  # Отправлен в г. транзит
# Зарегистрирована отправка в город-транзит. Проставлены дата и время отправления у перевозчика

WEBHOOK_ORDER_ACCEPTED_IN_TRANSIT_CITY = 22  # Встречен в г. транзите
# Зарегистрирована встреча в городе-транзите

WEBHOOK_ORDER_ACCEPTED_AT_TRANSIT_WAREHOUSE = 13  # Принят на склад транзита
# Оформлен приход в городе-транзите

WEBHOOK_ORDER_RETURNED_TO_TRANSIT_WAREHOUSE = 17  # Возвращен на склад транзита
# Повторно оформлен приход в городе-транзите (груз возвращен на склад).
# Примечание: этот статус не означает возврат груза отправителю.

WEBHOOK_ORDER_READY_FOR_SHIPMENT_IN_TRANSIT_CITY = 19  # Выдан на отправку в г. транзите
# Оформлен расход в городе-транзите

WEBHOOK_ORDER_TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY = 20  # Сдан перевозчику в г. транзите
# Зарегистрирована отправка у перевозчика в городе-транзите

WEBHOOK_ORDER_SENT_TO_SENDER_CITY = 27  # Отправлен в г. отправитель
# Зарегистрирована отправка в город-отправитель, груз в пути.

WEBHOOK_ORDER_SENT_TO_RECIPIENT_CITY = 8  # Отправлен в г. получатель
# Зарегистрирована отправка в город-получатель, груз в пути.

WEBHOOK_ORDER_ACCEPTED_IN_SENDER_CITY = 28  # Встречен в г. отправителе
# Зарегистрирована встреча груза в городе-отправителе

WEBHOOK_ORDER_ACCEPTED_IN_RECIPIENT_CITY = 9  # Встречен в г. получателе
# Зарегистрирована встреча груза в городе-получателе

WEBHOOK_ORDER_ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE = 10  # Принят на склад доставки
# Оформлен приход на склад города-получателя, ожидает доставки до двери

WEBHOOK_ORDER_ACCEPTED_AT_PICK_UP_POINT = 12  # Принят на склад до востребования
# Оформлен приход на склад города-получателя. Доставка до склада, посылка ожидает забора клиентом - покупателем ИМ

WEBHOOK_ORDER_TAKEN_BY_COURIER = 11  # Выдан на доставку
# Добавлен в курьерскую карту, выдан курьеру на доставку

WEBHOOK_ORDER_RETURNED_TO_RECIPIENT_CITY_WAREHOUSE = 18  # Возвращен на склад доставки
# Оформлен повторный приход на склад в городе-получателе. Доставка не удалась по какой-либо причине, ожидается очередная попытка доставки.
# Примечание: этот статус не означает возврат груза отправителю.

WEBHOOK_ORDER_DELIVERED = 4  # Вручен
# Успешно доставлен и вручен адресату (конечный статус).

WEBHOOK_ORDER_NOT_DELIVERED = 5  # Не вручен
# Покупатель отказался от покупки, возврат в ИМ (конечный статус).


# Document statuses

# квитанции | receipt
# ru: https://api-docs.cdek.ru/36967287.html - Приложение 1. Статусы квитанции
# en: https://api-docs.cdek.ru/36969694.html - Appendix 1. Receipt statuses

# ШК места | Barcode CP
# ru: https://api-docs.cdek.ru/36967298.html - Приложение 1. Статусы ШК места
# en: https://api-docs.cdek.ru/36969722.html - Appendix 1. Barcode CP statuses

DOCUMENT_ACCEPTED = "ACCEPTED"  # Принят | Запрос на формирование квитанции / ШК места принят
DOCUMENT_PROCESSING = "PROCESSING"  # Формируется | Файл с квитанцией / ШК места формируется
DOCUMENT_READY = "READY"  # Сформирован | Файл с квитанцией / ШК места и ссылка на скачивание файла сформированы
DOCUMENT_REMOVED = "REMOVED"  # Удален | Истекло время жизни ссылки на скачивание файла с квитанцией / ШК места
DOCUMENT_INVALID = "INVALID"  # Некорректный запрос | Некорректный запрос на формирование квитанции / ШК места
