# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-6.-Dopolnitelnye-uslugi
#
# created:   2022/04/14
# updated:   2026/09/26

INSURANCE = "INSURANCE"  # Страхование
TAKE_SENDER = "TAKE_SENDER"  # Забор в городе отправителе
DELIV_RECEIVER = "DELIV_RECEIVER"  # Доставка в городе получателе
TRYING_ON = "TRYING_ON"  # Примерка
PART_DELIV = "PART_DELIV"  # Частичная доставка
DANGER_CARGO = "DANGER_CARGO"  # Опасный груз
SMS = "SMS"  # Уведомление о вручении заказа
THERMAL_MODE = "THERMAL_MODE"  # Тепловой режим
COURIER_PACKAGE_A2 = "COURIER_PACKAGE_A2"  # Пакет курьерский А2
PACKAGE_A_2_LIGHT_EXPRESS = "PACKAGE_A_2_LIGHT_EXPRESS"  # Пакет курьерский «Лайт» А2 (белый)
PACKAGE_A_3_LIGHT_EXPRESS = "PACKAGE_A_3_LIGHT_EXPRESS"  # Пакет курьерский «Лайт» А3 (белый)
PACKAGE_A_4_LIGHT_EXPRESS = "PACKAGE_A_4_LIGHT_EXPRESS"  # Пакет курьерский «Лайт» А4 (белый)
PACKAGE_A_5_LIGHT_EXPRESS = "PACKAGE_A_5_LIGHT_EXPRESS"  # Пакет курьерский «Лайт» А5 (белый)
NOTIFY_ORDER_CREATED = "NOTIFY_ORDER_CREATED"  # Уведомление о создании заказа в СДЭК
NOTIFY_ORDER_DELIVERY = "NOTIFY_ORDER_DELIVERY"  # Уведомление о приеме заказа на доставку
CARTON_BOX_XS = "CARTON_BOX_XS"  # Коробка XS (0,5 кг 17х12х9 см)
CARTON_BOX_S_2_KILOS = "CARTON_BOX_S_2_KILOS"  # Коробка S (2 кг 23х19х10 см)
CARTON_BOX_M = "CARTON_BOX_M"  # Коробка M (5 кг 33х25х15 см)
CARTON_BOX_2KG = "CARTON_BOX_2KG"  # Коробка (2 кг 34х24х10 см)
CARTON_BOX_3KG = "CARTON_BOX_3KG"  # Коробка (3 кг 24х24х21 см)
CARTON_BOX_5KG = "CARTON_BOX_5KG"  # Коробка (5 кг 40х24х21 см)
CARTON_BOX_10KG = "CARTON_BOX_10KG"  # Коробка (10 кг 40х35х28 см)
CARTON_BOX_L_12_KILOS = "CARTON_BOX_L_12_KILOS"  # Коробка (12 кг 31х25х38 см)
CARTON_BOX_XL_18_KILOS = "CARTON_BOX_XL_18_KILOS"  # Коробка (18 кг 60х35х30 см)
CARTON_BOX_20KG = "CARTON_BOX_20KG"  # Коробка (20 кг 47х40х43 см)
CARTON_BOX_30KG = "CARTON_BOX_30KG"  # Коробка (30 кг 69х39х42 см)
BUBBLE_WRAP = "BUBBLE_WRAP"  # Воздушно-пузырчатая пленка
WASTE_PAPER = "WASTE_PAPER"  # Макулатурная бумага
CARTON_FILLER = "CARTON_FILLER"  # Прессованный картон "филлер" (55х14х2,3 см)
# Внутренние обрешётки передаются только в паре с соответствующей коробкой.
XL_BOX_INNER_CRATE = "XL_BOX_INNER_CRATE"  # Внутренняя обрешётка "Коробка XL"
BOX_20_KG_INNER_CRATE = "20_KG_BOX_INNER_CRATE"  # Внутренняя обрешётка "Коробка Вес до 20кг"
BOX_30_KG_INNER_CRATE = "30_KG_BOX_INNER_CRATE"  # Внутренняя обрешётка "Коробка Вес до 30кг"
BAN_ATTACHMENT_INSPECTION = "BAN_ATTACHMENT_INSPECTION"  # Запрет осмотра вложения
GET_UP_FLOOR_BY_HAND = "GET_UP_FLOOR_BY_HAND"  # Подъём на этаж (по лестнице)
DESCENT_FROM_THE_FLOOR = "DESCENT_FROM_THE_FLOOR"  # Спуск с этажа ручной (по лестнице)
GET_UP_FLOOR_BY_ELEVATOR = "GET_UP_FLOOR_BY_ELEVATOR"  # Подъём на этаж (на лифте)
ADULT_GOODS = "ADULT_GOODS"  # 18+
LOADING_OPERATIONS_AT_THE_SENDER = "LOADING_OPERATIONS_AT_THE_SENDER"  # Погрузо-разгрузочные работы у отправителя
LOAD_THE_OPERATION_AT_THE_RECIPIENT = "LOAD_THE_OPERATION_AT_THE_RECIPIENT"  # Погрузо-разгрузочные работы у получателя
GREEN_ENVELOPE_CDEK = "GREEN_ENVELOPE_CDEK"  # Конверт (картон, А4)
COURIER_SERVICE = "COURIER_SERVICE"  # Аренда курьера у отправителя
CUSTOMS_CLEARANCE = "CUSTOMS_CLEARANCE"  # Таможенное оформление
ANOTHER = "ANOTHER"  # Прочее. Начисляется менеджером СДЭК, передавать самостоятельно нельзя
SMS_NOTIFICATIONS_FOR_THE_RECIPIENT = "SMS_NOTIFICATIONS_FOR_THE_RECIPIENT"  # СМС-уведомление о прибытии заказа
SMS_NOTIFICATIONS_FOR_EXPIRATION_DATE = "SMS_NOTIFICATIONS_FOR_EXPIRATION_DATE"  # СМС-уведомление об окончании хранения
EXP_REGIST_WITH_DOC = "EXP_REGIST_WITH_DOC"  # Экспортное таможенное оформление (с документами)
EXP_REGIST_WITHOUT_DOC = "EXP_REGIST_WITHOUT_DOC"  # Экспортное таможенное оформление (без документов)
EXP_REGIST = "EXP_REGIST"  # Экспортное таможенное оформление
CUSTOM_CLEARENCE_FOR_LAST_MILE_B2B_200 = "CUSTOM_CLEARENCE_FOR_LAST_MILE_B2B_200"  # ТО последней мили B2B 200-
CUSTOMS_CLEARANCE_FOR_THE_LAST_MILE = "CUSTOMS_CLEARANCE_FOR_THE_LAST_MILE"  # ТО для последней мили
CUSTOM_CLEARENCE_FOR_LAST_MILE_B2B_200469 = "CUSTOM_CLEARENCE_FOR_LAST_MILE_B2B_200469"  # ТО последней мили B2B 200+
CUSTOM_CLEARENCE_FOR_B2B_1000_EXPORT = "CUSTOM_CLEARENCE_FOR_B2B_1000_EXPORT"  # Таможенное оформление B2B 1000+ экспорт
CUSTOM_CLEARENCE_FOR_B2B_200_IMPORT = "CUSTOM_CLEARENCE_FOR_B2B_200_IMPORT"  # Таможенное оформление B2B 200+ импорт
SELF_CLEARING_CUSTOMS_FOR_B2B_EXPORT = "SELF_CLEARING_CUSTOMS_FOR_B2B_EXPORT"  # Самостоятельное ТО B2B экспорт
SELF_CLEARING_CUSTOMS_FOR_B2B_IMPORT = "SELF_CLEARING_CUSTOMS_FOR_B2B_IMPORT"  # Самостоятельное ТО B2B импорт
PHOTO_OF_DOCUMENTS = "PHOTO_OF_DOCUMENTS"  # Фото документов
BOX_LINER_FOR_1_BOTTLE_UNIVERSAL = "BOX_LINER_FOR_1_BOTTLE_UNIVERSAL"  # Вкладыш для 1 бутылки (до 1 л.)
BOX_FOR_1_BOTTLE_3KG15X14X38CM = "BOX_FOR_1_BOTTLE_3KG15X14X38CM"  # Коробка для 1 бутылки (3кг 15х14х38см)
DOCUMENT_BOX_6KG36X29X7CM = "DOCUMENT_BOX_6KG36X29X7CM"  # Коробка Вес до 6кг (6кг 36х29х7см)
BOX_LIGHT_3KILOS35X25X12CM = "BOX_LIGHT_3KILOS35X25X12CM"  # Коробка Лайт 4 (3кг 35х25х12см)
BOX_LIGHT_8KILOS60X40X40CM = "BOX_LIGHT_8KILOS60X40X40CM"  # Коробка Лайт 1 (8кг 60х40х40см)

# В спецификации есть ещё услуги с числовыми кодами 42 (агентское вознаграждение) и 20 (пеня). Через интеграцию
# они не подключаются, поэтому констант для них нет.


# Нет в спецификации: отсутствуют в текущем списке услуг API. Сохранены для совместимости и будут пересмотрены
# при унификации констант в 3.0.0.

INSPECTION_CARGO = "INSPECTION_CARGO"  # Осмотр вложения
REVERSE = "REVERSE"  # Реверс
PACKAGE_1 = "PACKAGE_1"  # Упаковка 1
PACKAGE_2 = "PACKAGE_2"  # Упаковка 2
WAIT_FOR_RECEIVER = "WAIT_FOR_RECEIVER"  # Ожидание более 15 мин. у получателя
WAIT_FOR_SENDER = "WAIT_FOR_SENDER"  # Ожидание более 15 мин. у отправителя
REPEATED_DELIVERY = "REPEATED_DELIVERY"  # Повторная поездка
CALL = "CALL"  # Прозвон
SECURE_PACKAGE_A2 = "SECURE_PACKAGE_A2"  # Сейф пакет А2
SECURE_PACKAGE_A3 = "SECURE_PACKAGE_A3"  # Сейф пакет А3
SECURE_PACKAGE_A4 = "SECURE_PACKAGE_A4"  # Сейф пакет А4
SECURE_PACKAGE_A5 = "SECURE_PACKAGE_A5"  # Сейф пакет А5
CARTON_BOX_S = "CARTON_BOX_S"  # Коробка S (2 кг 21х20х11 см). В спецификации: `CARTON_BOX_S_2_KILOS`
CARTON_BOX_L = "CARTON_BOX_L"  # Коробка L (12 кг 34х33х26 см). В спецификации: `CARTON_BOX_L_12_KILOS`
CARTON_BOX_500GR = "CARTON_BOX_500GR"  # Коробка (0,5 кг 17х12х10 см)
CARTON_BOX_1KG = "CARTON_BOX_1KG"  # Коробка (1 кг 24х17х10 см)
CARTON_BOX_15KG = "CARTON_BOX_15KG"  # Коробка (15 кг 60х35х29 см)
PHOTO_DOCUMENT = "PHOTO_DOCUMENT"  # Фото документов. В спецификации: `PHOTO_OF_DOCUMENTS`
