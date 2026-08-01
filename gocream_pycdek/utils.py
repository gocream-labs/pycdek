import hashlib


def is_empty(value):
    return not (isinstance(value, (int, float)) or value not in (None, (), {}, ""))


def clear_dict(raw_dict, empty_data=is_empty):
    """
    Recurcive clear empty keys from dict

    Args:
        raw_dict (dict): raw dict
        empty_data (list|set, optioanl): set of empty values

    Returns:
        dict: Cleared dict
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
