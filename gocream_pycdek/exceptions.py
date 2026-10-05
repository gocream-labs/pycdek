from requests import PreparedRequest
from requests import RequestException
from requests import Response


class BaseCdekException(Exception):
    """
    Base class for all library exceptions

    Args:
        message (str, optional): Описание ошибки. По умолчанию - `default_message`.
        code (str, optional): Код ошибки. По умолчанию - `default_code`.
    """

    default_message = "Base CDEK exception."
    default_code = "base_cdek_exception"

    def __init__(self, message: str | None = None, code: str | None = None) -> None:
        self.code = code or self.default_code
        self.message = message or self.default_message

        super().__init__(f"Error {self.code}: {self.message}")


class CdekException(BaseCdekException):
    """
    Base class for client and API errors
    """

    default_message = "CDEK exception."
    default_code = "cdek_exception"


class CdekNoAuthClientException(CdekException):
    """
    Client credentials are not set
    """

    default_message = "Required auth client."
    default_code = "required_auth"


class CdekApiException(CdekException):
    """
    Authorization request failed
    """

    default_message = "CDEK api exception."
    default_code = "cdek_api_exception"


class CdekApiUnavailableException(CdekApiException):
    """
    API is temporarily unavailable
    """

    default_message = "CDEK api unavailable."
    default_code = "cdek_api_unavailable"


class CdekApiAccessException(CdekApiException):
    """
    API rejected client credentials
    """

    default_message = "CDEK bad api credentials."
    default_code = "cdek_bad_api_credentials"


class CdekApiWrongTokenTypeException(CdekApiException):
    """
    API returned an unsupported token type

    Args:
        token_type (str): Тип токена из ответа API.
        message (str, optional): Шаблон описания с плейсхолдером `{token_type}`. По умолчанию - `default_message`.
        code (str, optional): Код ошибки. По умолчанию - `default_code`.
    """

    default_message = "CDEK api returned token type `{token_type}` that not supported."
    default_code = "cdek_api_token_type"

    def __init__(self, token_type: str, message: str | None = None, code: str | None = None) -> None:
        super().__init__(
            (message or self.default_message).format(token_type=token_type),
            code or self.default_code,
        )


class CdekRequestException(BaseCdekException, RequestException):
    """
    HTTP request returned an error status

    Исходный ответ сохраняется в `response`.

    Args:
        message (str, optional): Описание ошибки. По умолчанию - `default_message`.
        code (str, optional): Код ошибки. По умолчанию - `default_code`.
        response (requests.Response, optional): Ответ, вызвавший ошибку.
        request (requests.PreparedRequest, optional): Запрос, вызвавший ошибку. По умолчанию берётся из `response`.
    """

    default_message = "CDEK request exception."
    default_code = "cdek_request_exception"

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        *,
        response: Response | None = None,
        request: PreparedRequest | None = None,
    ) -> None:
        # `RequestException.__init__` перетирает `response` и `request` тем, что найдёт в
        # своих kwargs, а `BaseCdekException` зовёт его через `super()` со строкой. Поэтому
        # атрибуты выставляются после родителя, иначе они молча обнулятся.
        super().__init__(message, code)

        self.response = response
        self.request = request if request is not None else getattr(response, "request", None)
