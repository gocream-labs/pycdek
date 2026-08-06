# Калькулятор

Расчёт стоимости доставки. `calculator_tariff` - актуальный метод API v2,
`get_shipping_cost` работает со снятым с поддержки калькулятором v1.5 и имеет
собственную схему авторизации через `authLogin` и `secure`.

[Раздел `calculator` в документации CDEK](https://apidoc.cdek.ru/#tag/calculator)

::: gocream_pycdek.client.CdekClient
    options:
      show_root_heading: false
      show_root_toc_entry: false
      members:
        - calculator_tariff
        - get_shipping_cost
