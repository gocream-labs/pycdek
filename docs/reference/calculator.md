# Калькулятор

Расчёт стоимости доставки. `calculator_tariff` - актуальный метод API v2,
[`get_shipping_cost`][gocream_pycdek.client.CdekClient.get_shipping_cost] использует калькулятор v1.5 и собственную схему авторизации через `authLogin` и `secure`.

Метод объявлен устаревшим с 2.0.0, выдаёт `DeprecationWarning` и будет удалён в 3.0.0. Для перехода на [`calculator_tariff`][gocream_pycdek.client.CdekClient.calculator_tariff] нужно адаптировать параметры: схемы запросов различаются.

[Раздел `calculator` в документации CDEK](https://apidoc.cdek.ru/#tag/calculator)

::: gocream_pycdek.client.CdekClient
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - calculator_tariff
        - get_shipping_cost
