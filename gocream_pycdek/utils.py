import hashlib


def is_empty(value):
    """
    Tell whether a value counts as empty for `clear_dict`

    Deprecated:
        2.0.0: Предикат существует только ради
            [`clear_dict`][gocream_pycdek.utils.clear_dict] и уходит вместе с ним.

    Правило непоследовательно и таким и останется — его чинить некуда, потому что
    сама идея признана неверной. `()` пустой, а `[]` нет; `0`, `0.0` и `False`
    спасает отдельная проверка на число, а `""` такой проверки не получил.

    Args:
        value: Проверяемое значение.

    Returns:
        bool: `True`, если значение считается пустым.
    """

    return not (isinstance(value, (int, float)) or value not in (None, (), {}, ""))


def drop_none(fields):
    """
    Build request payload from named parameters, keeping only the ones that were passed

    Необязательный параметр метода клиента по умолчанию равен `None`, и это значит
    ровно одно: пользователь его не передал, в теле запроса ключа быть не должно.
    Обратное тоже верно — всё, что передали, уходит как есть.

    В отличие от [`clear_dict`][gocream_pycdek.utils.clear_dict] функция не считает
    `""`, `{}` или `[]` пустыми и не спускается во вложенные структуры: пустая строка
    в СДЭК означает сброс поля, а не его отсутствие, и решать за пользователя, что
    именно он имел в виду, клиент не должен.

    Args:
        fields (dict): Поля тела запроса вместе с непереданными.

    Returns:
        dict: Поля без тех, что равны `None`.
    """

    return {key: value for key, value in fields.items() if value is not None}


def clear_dict(raw_dict, empty_data=is_empty):
    """
    Recursively clear empty keys from dict

    Deprecated:
        2.0.0: Используйте [`drop_none`][gocream_pycdek.utils.drop_none]. Функция
            будет удалена в 3.0.0.

    Тело запроса собирается из непереданных параметров, а не из «пустых» значений:
    `None` означает «параметра не было», тогда как `""` и `{}` пользователь передал
    осознанно. Выкидывать их — значит решать за него; в частности, сброс поля пустой
    строкой через клиент становится невозможен.

    Вдобавок очистка применяется неравномерно: словарь внутри списка не обходится,
    поэтому основная часть тела заказа — `packages` и `items` — проходит мимо неё.

    Пока функция остаётся: на неё опираются ещё не переработанные методы клиента.
    Предупреждения в рантайме поэтому нет — оно прилетало бы пользователю за наш
    собственный вызов, на который он повлиять не может. Появится, когда уйдёт
    последний внутренний вызов.

    Args:
        raw_dict (dict): Исходный словарь.
        empty_data (callable, optional): Предикат «значение пустое». Применяется
            только к верхнему уровню: рекурсивный вызов идёт с предикатом по
            умолчанию. Defaults to `is_empty`.

    Returns:
        dict: Словарь без пустых значений.
    """

    new_dict = {}

    for k, v in raw_dict.items():
        if isinstance(v, dict) and not empty_data(v):
            new_v = clear_dict(v)

            if not empty_data(new_v):
                new_dict[k] = new_v

        elif not empty_data(v):
            new_dict[k] = v

    return new_dict


def get_secure(secure_password, date):
    code = f"{date}&{secure_password}".encode()
    return hashlib.md5(code).hexdigest()
