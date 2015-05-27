
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


class NewPasswordsMismatch(CommonException):
    message = "Новый пароль и его подтверждение не совпадают."

# noinspection PyDocstring
class AuthorizationError(CommonException):
    message = "Ошибка авторизации"


class IncorrectVerificationCode(CommonException):
    message = "Код верификации указан неправильно"


class IncorrectVerificationCodeFatal(CommonException):
    message = "Сбой верификации. Процедуру придется повторить с самого начала."


class AlreadyRegistred(CommonException):
    message = "Вы уже зарегистрированы в системе. " \
              "Если Вы не помните свой пароль - воспользуйтесь возможностью восстановления пароля: " \
              "новый пароль будет выслан Вам в смс-сообщении."


class SmsError(CommonException):
    message = "По техническим причинам отправка смс-сообщений, " \
              "а следовательно и авторизация/восстановление пароля временно недоступны. "\
              "Приносим свои извинения за доставленные неудобства!"


class NotRegisteredYet(CommonException):
    message = "Пользователь с таким телефоном еще не зарегистрирован в системе"


class EmailIsVerified(CommonException):
    message = "Ваш email уже подтвержден ранее, вы можете получить пароль по электронной почте"