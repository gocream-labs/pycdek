#
# See the full list of errors in the CDEK documentation:
# docs: https://apidoc.cdek.ru/#tag/common/Spisok-vozmozhnyh-oshibok
#
# created:   2022/04/15

# Internal error
# Запрос выполнился с системной ошибкой
V2_INTERNAL_ERROR = "v2_internal_error"

# Bad request
# некорректный запрос
V2_BAD_REQUEST = "v2_bad_request"


# additional errors not described in the documentation:

# Неверно задан тип тарифа
ERR_INVALID_TARIFFTYPECODE = "ERR_INVALID_TARIFFTYPECODE"

# По данному направлению при заданных условиях выбранный тариф недоступен
ERR_RESULT_SERVICE_EMPTY = "ERR_RESULT_SERVICE_EMPTY"

# В указанную дату создания заказа выбранная услуга не доступна
ERR_INVALID_TARIFF_WITH_DATETIMEORDERSEND = "ERR_INVALID_TARIFF_WITH_DATETIMEORDERSEND"
