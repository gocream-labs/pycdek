from requests import RequestException


class BaseCdekException(Exception):
    default_message = "Base CDEK exception."
    default_code = "base_cdek_exception"

    def __init__(self, message=None, code=None):
        self.code = code or self.default_code
        self.message = message or self.default_message

        super().__init__(f"Error {self.code}: {self.message}")


class CdekException(BaseCdekException):
    """
    General exception
    """

    default_message = "CDEK exception."
    default_code = "cdek_exception"


class CdekNoAuthClientException(CdekException):
    """
    Client need to be authed
    """

    default_message = "Required auth client."
    default_code = "required_auth"


class CdekApiException(CdekException):
    """
    Base API exception
    """

    default_message = "CDEK api exception."
    default_code = "cdek_api_exception"


class CdekApiUnavailableException(CdekApiException):
    """
    API Unavailable error
    """

    default_message = "CDEK api unavailable."
    default_code = "cdek_api_unavailable"


class CdekApiAccessException(CdekApiException):
    """
    API access error
    """

    default_message = "CDEK bad api credentials."
    default_code = "cdek_bad_api_credentials"


class CdekApiWrongTokenTypeException(CdekApiException):
    """
    API Token Type error
    """

    default_message = "CDEK api returned token type `{token_type}` that not supported."
    default_code = "cdek_api_token_type"

    def __init__(self, token_type, message=None, code=None):
        super().__init__(
            (message or self.default_message).format(token_type=token_type),
            code or self.default_code,
        )


class CdekRequestException(BaseCdekException, RequestException):
    """
    Wrapper around `RequestException` so we can catch them separatly
    """

    default_message = "CDEK request exception."
    default_code = "cdek_request_exception"

    def __init__(self, message=None, code=None, *, response=None, request=None):
        """
        Args:
            message: Human readable description, `default_message` if omitted.
            code: Machine readable code, `default_code` if omitted.
            response: Response that caused the error, if there was one.
            request: Request that caused the error, taken from `response` if omitted.
        """

        # `RequestException.__init__` перетирает `response` и `request` тем, что найдёт в
        # своих kwargs, а `BaseCdekException` зовёт его через `super()` со строкой. Поэтому
        # атрибуты выставляются после родителя, иначе они молча обнулятся.
        super().__init__(message, code)

        self.response = response
        self.request = request if request is not None else getattr(response, "request", None)
