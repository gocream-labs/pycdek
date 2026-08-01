#
# updated:   2022/04/15
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


# INTERNET SHOP #
# INTERNET SHOP - IS
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK

IS_INTERNATIONAL_EXPRESS_DOCS = 7  # Международный экспресс документы дверь-дверь
IS_INTERNATIONAL_EXPRESS = 8  # Международный экспресс грузы дверь-дверь

IS_REGULAR_WW = 136  # Посылка склад-склад
IS_REGULAR_WD = 137  # Посылка склад-дверь
IS_REGULAR_DW = 138  # Посылка дверь-склад
IS_REGULAR_DD = 139  # Посылка дверь-дверь

IS_INTERNATIONAL_EXPRESS_WW = 178  # DEPRECATED!!! Международный экспресс грузы склад-склад
IS_INTERNATIONAL_EXPRESS_WD = 179  # DEPRECATED!!! Международный экспресс грузы склад-дверь
IS_INTERNATIONAL_EXPRESS_DW = 180  # DEPRECATED!!! Международный экспресс грузы дверь-склад

IS_INTERNATIONAL_EXPRESS_DOCS_WW = 181  # DEPRECATED!!! Международный экспресс документы склад-склад
IS_INTERNATIONAL_EXPRESS_DOCS_WD = 182  # DEPRECATED!!! Международный экспресс документы склад-дверь
IS_INTERNATIONAL_EXPRESS_DOCS_DW = 183  # DEPRECATED!!! Международный экспресс документы дверь-склад

IS_ECONOMY_DD = 231  # DEPRECATED!!! Экономичная посылка дверь-дверь
IS_ECONOMY_DW = 232  # DEPRECATED!!! Экономичная посылка дверь-склад
IS_ECONOMY_WD = 233  # Экономичная посылка склад-дверь
IS_ECONOMY_WW = 234  # Экономичная посылка склад-склад

IS_EXPRESS_WW = 291  # CDEK Express склад-склад
IS_EXPRESS_DD = 293  # CDEK Express дверь-дверь
IS_EXPRESS_WD = 294  # CDEK Express склад-дверь
IS_EXPRESS_DW = 295  # CDEK Express дверь-склад

IS_REGULAR_DP = 366  # Посылка дверь-постамат
IS_REGULAR_WP = 368  # Посылка склад-постамат

IS_ECONOMY_DP = 376  # DEPRECATED!!! Экономичная посылка дверь-постамат
IS_ECONOMY_WP = 378  # Экономичная посылка склад-постамат

# END OF INTERNET SHOP #


# CHINA EXPRESS #
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK

CHINA_EXPRESS_WW = 243  # Китайский экспресс склад-склад
CHINA_EXPRESS_DD = 245  # Китайский экспресс дверь-дверь
CHINA_EXPRESS_WD = 246  # Китайский экспресс склад-дверь
CHINA_EXPRESS_DW = 247  # Китайский экспресс дверь-склад

# END OF CHINA EXPRESS #


# BASE #
# docs: https://apidoc.cdek.ru/#tag/common/Prilozheniya/Prilozhenie-4.-Tarify-SDEK

# Классическая экспресс-доставка по России документов и грузов до 30 кг.
BASE_EXPRESS_LITE_DD = 1  # Экспресс лайт дверь-дверь
BASE_EXPRESS_LITE_DP = 361  # Экспресс лайт дверь-постамат
BASE_EXPRESS_LITE_WP = 363  # Экспресс лайт склад-постамат
# Классическая экспресс-доставка по России документов и грузов.
BASE_EXPRESS_LITE_WW = 10  # Экспресс лайт склад-склад
BASE_EXPRESS_LITE_WD = 11  # Экспресс лайт склад-дверь
BASE_EXPRESS_LITE_DW = 12  # Экспресс лайт дверь-склад

# Срочная доставка документов и грузов «из рук в руки» по России к определенному часу.
BASE_SUPER_EXPRESS_TO_18 = 3  # Супер-экспресс до 18 дверь-дверь
# Срочная доставка документов и грузов «из рук в руки» по России к определенному часу (доставка за 1-2 суток).
BASE_SUPER_EXPRESS_TO_9 = 57  # Супер-экспресс до 9 дверь-дверь
BASE_SUPER_EXPRESS_TO_10 = 58  # Супер-экспресс до 10 дверь-дверь
BASE_SUPER_EXPRESS_TO_12 = 59  # Супер-экспресс до 12 дверь-дверь
BASE_SUPER_EXPRESS_TO_14 = 60  # Супер-экспресс до 14 дверь-дверь
BASE_SUPER_EXPRESS_TO_16 = 61  # Супер-экспресс до 16 дверь-дверь

# Классическая экспресс-доставка по России грузов.
BASE_EXPRESS_HEAVYWEIGHTS_WW = 15  # Экспресс тяжеловесы склад-склад
BASE_EXPRESS_HEAVYWEIGHTS_WD = 16  # Экспресс тяжеловесы склад-дверь
BASE_EXPRESS_HEAVYWEIGHTS_DW = 17  # Экспресс тяжеловесы дверь-склад
BASE_EXPRESS_HEAVYWEIGHTS_DD = 18  # Экспресс тяжеловесы дверь-дверь

# Недорогая доставка грузов по России ЖД и автотранспортом (доставка грузов с увеличением сроков).
BASE_ECONOMY_EXPRESS_WW = 5  # Экономичный экспресс склад-склад
BASE_ECONOMY_EXPRESS_DD = 118  # Экономичный экспресс дверь-дверь
BASE_ECONOMY_EXPRESS_WD = 119  # Экономичный экспресс склад-дверь
BASE_ECONOMY_EXPRESS_DW = 120  # Экономичный экспресс дверь-склад

# Быстрая экономичная доставка грузов по России
BASE_MAGISTRAL_EXPRESS_WW = 62  # Магистральный экспресс склад-склад
BASE_MAGISTRAL_EXPRESS_DD = 121  # Магистральный экспресс дверь-дверь
BASE_MAGISTRAL_EXPRESS_WD = 122  # Магистральный экспресс склад-дверь
BASE_MAGISTRAL_EXPRESS_DW = 123  # Магистральный экспресс дверь-склад

# Быстрая экономичная доставка грузов к определенному часу
BASE_MAGISTRAL_SUPER_EXPRESS_WW = 63  # Магистральный супер-экспресс склад-склад
BASE_MAGISTRAL_SUPER_EXPRESS_DD = 124  # Магистральный супер-экспресс дверь-дверь
BASE_MAGISTRAL_SUPER_EXPRESS_WD = 125  # Магистральный супер-экспресс склад-дверь
BASE_MAGISTRAL_SUPER_EXPRESS_DW = 126  # Магистральный супер-экспресс дверь-склад

# Классическая экспресс-доставка документов и грузов по стандартным срокам доставки внутри страны
# (Россия, Белоруссия, Армения, Киргизия, Казахстан). Также действует по направлениям между странами
# таможенного союза (Россия, Белоруссия, Армения, Киргизия, Казахстан).
# Без ограничений по весу
BASE_INTERNATIONAL_EXPRESS_DD = 480  # Экспресс дверь-дверь
BASE_INTERNATIONAL_EXPRESS_DW = 481  # Экспресс дверь-склад
BASE_INTERNATIONAL_EXPRESS_WD = 482  # Экспресс склад-дверь
BASE_INTERNATIONAL_EXPRESS_WW = 483  # Экспресс склад-склад
BASE_INTERNATIONAL_EXPRESS_DP = 485  # Экспресс дверь-постамат
BASE_INTERNATIONAL_EXPRESS_WP = 486  # Экспресс склад-постамат

# END OF BASE #
