#
# updated:   2026/09/26
#
# W - Warehouse
# D - Door
# P - Parcel machine

# WW - Warehouse - Warehouse
# WD - Warehouse - Door
# DW - Door - Warehouse
# DD - Door - Door
# WP - Warehouse - Parcel machine
# etc.
#
# Таблица тарифов в спецификации носит справочный характер: актуальный список тарифов по договору
# возвращает метод "Список доступных тарифов".
#
# Константы с пометкой "нет в спецификации" отсутствуют в текущей таблице тарифов API.
# Они сохранены для совместимости и будут пересмотрены при унификации констант в 3.0.0.


# INTERNET SHOP #
# INTERNET SHOP - IS
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK

IS_INTERNATIONAL_EXPRESS_DOCS = 7  # Международный экспресс документы дверь-дверь
IS_INTERNATIONAL_EXPRESS = 8  # Международный экспресс грузы дверь-дверь

IS_REGULAR_WW = 136  # Посылка склад-склад
IS_REGULAR_WD = 137  # Посылка склад-дверь
IS_REGULAR_DW = 138  # Посылка дверь-склад
IS_REGULAR_DD = 139  # Посылка дверь-дверь
IS_REGULAR_DP = 366  # Посылка дверь-постамат
IS_REGULAR_WP = 368  # Посылка склад-постамат

IS_RETURN_WW = 140  # Возврат склад-склад
IS_RETURN_WD = 141  # Возврат склад-дверь

IS_INTERNATIONAL_EXPRESS_WW = 178  # Нет в спецификации. Международный экспресс грузы склад-склад
IS_INTERNATIONAL_EXPRESS_WD = 179  # Нет в спецификации. Международный экспресс грузы склад-дверь
IS_INTERNATIONAL_EXPRESS_DW = 180  # Нет в спецификации. Международный экспресс грузы дверь-склад

IS_INTERNATIONAL_EXPRESS_DOCS_WW = 181  # Нет в спецификации. Международный экспресс документы склад-склад
IS_INTERNATIONAL_EXPRESS_DOCS_WD = 182  # Нет в спецификации. Международный экспресс документы склад-дверь
IS_INTERNATIONAL_EXPRESS_DOCS_DW = 183  # Нет в спецификации. Международный экспресс документы дверь-склад

IS_ECONOMY_DD = 231  # Экономичная посылка дверь-дверь
IS_ECONOMY_DW = 232  # Экономичная посылка дверь-склад
IS_ECONOMY_WD = 233  # Экономичная посылка склад-дверь
IS_ECONOMY_WW = 234  # Экономичная посылка склад-склад
IS_ECONOMY_DP = 376  # Нет в спецификации. Экономичная посылка дверь-постамат
IS_ECONOMY_WP = 378  # Экономичная посылка склад-постамат

# Экспресс-доставка авиа товаров из-за рубежа с таможенным оформлением. Только для юридических лиц.
IS_EXPRESS_WW = 291  # E-com Express склад-склад
IS_EXPRESS_DD = 293  # E-com Express дверь-дверь
IS_EXPRESS_WD = 294  # E-com Express склад-дверь
IS_EXPRESS_DW = 295  # E-com Express дверь-склад
IS_EXPRESS_DP = 509  # E-com Express дверь-постамат
IS_EXPRESS_WP = 510  # E-com Express склад-постамат
# Второй набор кодов E-com Express: в спецификации название с точкой, отличие от 291 и 293 не описано.
IS_EXPRESS_2_DD = 2483  # E-com Express. дверь-дверь
IS_EXPRESS_2_WW = 2485  # E-com Express. склад-склад

# Стандартная доставка товаров из-за рубежа с таможенным оформлением. Только для юридических лиц.
IS_STANDARD_DD = 184  # E-com Standard дверь-дверь
IS_STANDARD_WW = 185  # E-com Standard склад-склад
IS_STANDARD_WD = 186  # E-com Standard склад-дверь
IS_STANDARD_DW = 187  # E-com Standard дверь-склад
IS_STANDARD_DP = 497  # E-com Standard дверь-постамат
IS_STANDARD_WP = 498  # E-com Standard склад-постамат

# Быстрая международная доставка документов.
IS_DOCUMENTS_EXPRESS_DD = 2261  # Documents Express дверь-дверь
IS_DOCUMENTS_EXPRESS_DW = 2262  # Documents Express дверь-склад
IS_DOCUMENTS_EXPRESS_WD = 2263  # Documents Express склад-дверь
IS_DOCUMENTS_EXPRESS_WW = 2264  # Documents Express склад-склад
IS_DOCUMENTS_EXPRESS_DP = 2266  # Documents Express дверь-постамат
IS_DOCUMENTS_EXPRESS_WP = 2267  # Documents Express склад-постамат

# Экономичная доставка шин. Требует дополнительного типа заказа "10" в `additional_order_types`.
IS_ECONOMY_EXPRESS_DD = 19  # Экономичный экспресс дверь-дверь
IS_ECONOMY_EXPRESS_DW = 2321  # Экономичный экспресс дверь-склад
IS_ECONOMY_EXPRESS_WD = 2322  # Экономичный экспресс склад-дверь
IS_ECONOMY_EXPRESS_WW = 2323  # Экономичный экспресс склад-склад

IS_SAME_DAY_DD = 2360  # Доставка день в день

# Тарифы ниже перечислены в спецификации и среди тарифов для ИМ, и среди тарифов обычной доставки.
IS_ONE_OFFICE_WW = 2536  # Один офис (ИМ)
IS_FULFILLMENT_PICKUP_WW = 358  # Фулфилмент выдача

# END OF INTERNET SHOP #


# CHINA EXPRESS #
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK
# Нет в спецификации: весь раздел.

CHINA_EXPRESS_WW = 243  # Китайский экспресс склад-склад
CHINA_EXPRESS_DD = 245  # Китайский экспресс дверь-дверь
CHINA_EXPRESS_WD = 246  # Китайский экспресс склад-дверь
CHINA_EXPRESS_DW = 247  # Китайский экспресс дверь-склад

# END OF CHINA EXPRESS #


# BASE #
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK

# Нет в спецификации. Классическая экспресс-доставка по России документов и грузов до 30 кг.
BASE_EXPRESS_LITE_DD = 1  # Экспресс лайт дверь-дверь
BASE_EXPRESS_LITE_DP = 361  # Экспресс лайт дверь-постамат
BASE_EXPRESS_LITE_WP = 363  # Экспресс лайт склад-постамат
# Нет в спецификации. Классическая экспресс-доставка по России документов и грузов.
BASE_EXPRESS_LITE_WW = 10  # Экспресс лайт склад-склад
BASE_EXPRESS_LITE_WD = 11  # Экспресс лайт склад-дверь
BASE_EXPRESS_LITE_DW = 12  # Экспресс лайт дверь-склад

# Срочная доставка документов и грузов «из рук в руки» к определенному часу (доставка за сутки). До 30 кг.
BASE_SUPER_EXPRESS_TO_18 = 3  # Супер-экспресс до 18 дверь-дверь
BASE_SUPER_EXPRESS_TO_9 = 57  # Нет в спецификации. Супер-экспресс до 9 дверь-дверь
BASE_SUPER_EXPRESS_TO_10 = 58  # Супер-экспресс до 10 дверь-дверь
BASE_SUPER_EXPRESS_TO_12 = 59  # Супер-экспресс до 12 дверь-дверь
BASE_SUPER_EXPRESS_TO_14 = 60  # Супер-экспресс до 14 дверь-дверь
BASE_SUPER_EXPRESS_TO_16 = 61  # Супер-экспресс до 16 дверь-дверь
BASE_SUPER_EXPRESS_TO_12_DW = 777  # Супер-экспресс до 12 дверь-склад
BASE_SUPER_EXPRESS_TO_12_WD = 778  # Супер-экспресс до 12 склад-дверь
BASE_SUPER_EXPRESS_TO_12_WW = 779  # Супер-экспресс до 12 склад-склад
BASE_SUPER_EXPRESS_TO_14_DW = 786  # Супер-экспресс до 14 дверь-склад
BASE_SUPER_EXPRESS_TO_14_WD = 787  # Супер-экспресс до 14 склад-дверь
BASE_SUPER_EXPRESS_TO_14_WW = 788  # Супер-экспресс до 14 склад-склад
BASE_SUPER_EXPRESS_TO_16_DW = 795  # Супер-экспресс до 16 дверь-склад
BASE_SUPER_EXPRESS_TO_16_WD = 796  # Супер-экспресс до 16 склад-дверь
BASE_SUPER_EXPRESS_TO_16_WW = 797  # Супер-экспресс до 16 склад-склад
BASE_SUPER_EXPRESS_TO_18_DW = 804  # Супер-экспресс до 18 дверь-склад
BASE_SUPER_EXPRESS_TO_18_WD = 805  # Супер-экспресс до 18 склад-дверь
BASE_SUPER_EXPRESS_TO_18_WW = 806  # Супер-экспресс до 18 склад-склад
BASE_SUPER_EXPRESS_TO_18_WP = 722  # Супер-экспресс до 18 склад-постамат

# Срочная доставка документов и грузов «из рук в руки» к определенному часу (доставка за 1-2 суток). До 30 кг.
BASE_SUPER_EXPRESS_TO_10_00_DD = 676  # Супер-экспресс до 10.00 дверь-дверь
BASE_SUPER_EXPRESS_TO_10_00_DW = 677  # Супер-экспресс до 10.00 дверь-склад
BASE_SUPER_EXPRESS_TO_10_00_WD = 678  # Супер-экспресс до 10.00 склад-дверь
BASE_SUPER_EXPRESS_TO_10_00_WW = 679  # Супер-экспресс до 10.00 склад-склад
BASE_SUPER_EXPRESS_TO_12_00_DD = 686  # Супер-экспресс до 12.00 дверь-дверь
BASE_SUPER_EXPRESS_TO_12_00_DW = 687  # Супер-экспресс до 12.00 дверь-склад
BASE_SUPER_EXPRESS_TO_12_00_WD = 688  # Супер-экспресс до 12.00 склад-дверь
BASE_SUPER_EXPRESS_TO_12_00_WW = 689  # Супер-экспресс до 12.00 склад-склад
BASE_SUPER_EXPRESS_TO_14_00_DD = 696  # Супер-экспресс до 14.00 дверь-дверь
BASE_SUPER_EXPRESS_TO_14_00_DW = 697  # Супер-экспресс до 14.00 дверь-склад
BASE_SUPER_EXPRESS_TO_14_00_WD = 698  # Супер-экспресс до 14.00 склад-дверь
BASE_SUPER_EXPRESS_TO_14_00_WW = 699  # Супер-экспресс до 14.00 склад-склад
BASE_SUPER_EXPRESS_TO_16_00_DD = 706  # Супер-экспресс до 16.00 дверь-дверь
BASE_SUPER_EXPRESS_TO_16_00_DW = 707  # Супер-экспресс до 16.00 дверь-склад
BASE_SUPER_EXPRESS_TO_16_00_WD = 708  # Супер-экспресс до 16.00 склад-дверь
BASE_SUPER_EXPRESS_TO_16_00_WW = 709  # Супер-экспресс до 16.00 склад-склад
BASE_SUPER_EXPRESS_TO_18_00_DD = 716  # Супер-экспресс до 18.00 дверь-дверь
BASE_SUPER_EXPRESS_TO_18_00_DW = 717  # Супер-экспресс до 18.00 дверь-склад
BASE_SUPER_EXPRESS_TO_18_00_WD = 718  # Супер-экспресс до 18.00 склад-дверь
BASE_SUPER_EXPRESS_TO_18_00_WW = 719  # Супер-экспресс до 18.00 склад-склад

# Нет в спецификации. Классическая экспресс-доставка по России грузов.
BASE_EXPRESS_HEAVYWEIGHTS_WW = 15  # Экспресс тяжеловесы склад-склад
BASE_EXPRESS_HEAVYWEIGHTS_WD = 16  # Экспресс тяжеловесы склад-дверь
BASE_EXPRESS_HEAVYWEIGHTS_DW = 17  # Экспресс тяжеловесы дверь-склад
BASE_EXPRESS_HEAVYWEIGHTS_DD = 18  # Экспресс тяжеловесы дверь-дверь

# Нет в спецификации. Недорогая доставка грузов по России ЖД и автотранспортом.
# Экономичный экспресс в спецификации есть только в тарифах для ИМ, с другими кодами: см. `IS_ECONOMY_EXPRESS_*`.
BASE_ECONOMY_EXPRESS_WW = 5  # Экономичный экспресс склад-склад
BASE_ECONOMY_EXPRESS_DD = 118  # Экономичный экспресс дверь-дверь
BASE_ECONOMY_EXPRESS_WD = 119  # Экономичный экспресс склад-дверь
BASE_ECONOMY_EXPRESS_DW = 120  # Экономичный экспресс дверь-склад

# Быстрая экономичная доставка грузов.
BASE_MAGISTRAL_EXPRESS_WW = 62  # Магистральный экспресс склад-склад
BASE_MAGISTRAL_EXPRESS_DD = 121  # Магистральный экспресс дверь-дверь
BASE_MAGISTRAL_EXPRESS_WD = 122  # Магистральный экспресс склад-дверь
BASE_MAGISTRAL_EXPRESS_DW = 123  # Магистральный экспресс дверь-склад

# Нет в спецификации. Быстрая экономичная доставка грузов к определенному часу.
BASE_MAGISTRAL_SUPER_EXPRESS_WW = 63  # Магистральный супер-экспресс склад-склад
BASE_MAGISTRAL_SUPER_EXPRESS_DD = 124  # Магистральный супер-экспресс дверь-дверь
BASE_MAGISTRAL_SUPER_EXPRESS_WD = 125  # Магистральный супер-экспресс склад-дверь
BASE_MAGISTRAL_SUPER_EXPRESS_DW = 126  # Магистральный супер-экспресс дверь-склад

# Классическая экспресс-доставка документов и грузов по стандартным срокам доставки. Без ограничений по весу.
BASE_INTERNATIONAL_EXPRESS_DD = 480  # Экспресс дверь-дверь
BASE_INTERNATIONAL_EXPRESS_DW = 481  # Экспресс дверь-склад
BASE_INTERNATIONAL_EXPRESS_WD = 482  # Экспресс склад-дверь
BASE_INTERNATIONAL_EXPRESS_WW = 483  # Экспресс склад-склад
BASE_INTERNATIONAL_EXPRESS_DP = 485  # Экспресс дверь-постамат
BASE_INTERNATIONAL_EXPRESS_WP = 486  # Экспресс склад-постамат
BASE_INTERNATIONAL_EXPRESS_PD = 605  # Экспресс постамат-дверь
BASE_INTERNATIONAL_EXPRESS_PW = 606  # Экспресс постамат-склад
BASE_INTERNATIONAL_EXPRESS_PP = 607  # Экспресс постамат-постамат

# Экономичная наземная доставка сборных грузов от 60 кг. Требует дополнительного типа заказа "2" - "Сборный груз".
BASE_CONSOLIDATED_CARGO_DD = 748  # Сборный груз дверь-дверь
BASE_CONSOLIDATED_CARGO_DW = 749  # Сборный груз дверь-склад
BASE_CONSOLIDATED_CARGO_WD = 750  # Сборный груз склад-дверь
BASE_CONSOLIDATED_CARGO_WW = 751  # Сборный груз склад-склад

# Экспресс-доставка документов до 0,5 кг. Только для заказов с типом "доставка".
BASE_CDEK_DOCUMENTS_DD = 533  # СДЭК документы дверь-дверь
BASE_CDEK_DOCUMENTS_DW = 534  # СДЭК документы дверь-склад
BASE_CDEK_DOCUMENTS_WD = 535  # СДЭК документы склад-дверь
BASE_CDEK_DOCUMENTS_WW = 536  # СДЭК документы склад-склад

# END OF BASE #
