
from z9.core.exceptions import CommonException


# noinspection PyDocstring
class NoLoginForAccount(CommonException):
    message = "Не указан логин для нового аккаунта"


# noinspection PyDocstring
class NoPasswordForAccount(CommonException):
    message = "Не указан пароль для нового аккаунта"


# noinspection PyDocstring
class WrongTypeForAccount(CommonException):
    message = "Указан некорректный тип аккаунта"


# noinspection PyDocstring
class DublicateLogin(CommonException):
    message = "Указанный логин уже используется в системе"


# noinspection PyDocstring
class IncorrectLogin(CommonException):
    message = "Ошибка аутентификации. Некорректно указан логин."


# noinspection PyDocstring
class IncorrectPassword(CommonException):
    message = "Ошибка аутентификации. Некорректно указан пароль."


# noinspection PyDocstring
class IncorrectToken(CommonException):
    message = "Ошибка аутентификации. Некорректно указан токен."


# noinspection PyDocstring
class NoDataForAuth(CommonException):
    message = "Ошибка аутентификации. Недостаточно данных для аутентификации."


# noinspection PyDocstring
class AuthorizationError(CommonException):
    message = "Ошибка авторизации"