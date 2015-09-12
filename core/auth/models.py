
"""
Модели пакета sf.auth, отвечающие за аутентификационно-авторизационный слой системы

"""

import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

from mapex import EntityModel, CollectionModel
from envi import Request
from z9.core.auth.mappers import AccountsMapper, AccountSettingsMapper
from z9.core.auth.exceptions import *
from z9.core.utils import md5, flexdict, flat_dict
from mapex.src.Utils import do_dict, merge_dict


class Accounts(CollectionModel):
    """ Класс для работы с коллекцией учетных записей """
    mapper = AccountsMapper


class Account(EntityModel):
    """ Класс для работы с сущностью учтеной записи """
    mapper = AccountsMapper

    @property
    def password(self):
        """ Password property """
        return self.password_raw

    @password.setter
    def password(self, value):
        """
        Устанавливает пароль в зашифрованном виде
        @param value: Пароль в исходном виде
        """
        # noinspection PyAttributeOutsideInit
        self.password_raw = md5(value)

    def set_new_token(self) -> str:
        """
        Генерирует новый токен для аккаунта и сохраняет его
        @return: Новый сгенерированный токен аккаунта
        """
        # noinspection PyAttributeOutsideInit
        self.token = md5("%s%d" % (str(datetime.now()), random.choice(range(100))))
        self.save()
        return self.token

    @property
    def settings(self):
        if not hasattr(self, "_settings"):
            self._settings = flexdict()
            for setting in self.settings_raw:
                self._settings = merge_dict(self._settings, do_dict(setting.name, setting.value, cls=flexdict), cls=flexdict)
        return self._settings

    def save_settings(self):
        self.mark_as_changed()
        return self.save()

    def validate(self):
        """
        Валидация сущности учетной записи
        @raise NoLoginForAccount: Если не указан логин
        @raise NoPasswordForAccount: Если не указан пароль
        """
        if not self.login or len(self.login) == 0:
            raise NoLoginForAccount()
        if not self.password_raw or self.password_raw == "d41d8cd98f00b204e9800998ecf8427e":
            raise NoPasswordForAccount()

        self.settings_raw = [
            AccountSetting({"name": name, "value": str(value)}) for name, value in flat_dict(self.settings).items()
        ]


class AccountSettings(CollectionModel):
    mapper = AccountSettingsMapper


class AccountSetting(EntityModel):
    mapper = AccountSettingsMapper


class AuthentificationService(object):
    """ Сервис первичной аутентификации пользователей

    При удачной аутентификации сервис возвращает экземпляр аккаунта,
    под которым пользователь аутентифицирован

    """
    smtp_config = None

    @classmethod
    def authentificate(cls, credentials: tuple=None, token: str=None) -> Account:
        """
        Выполняет аутентификацию пользователя по переданным данным
        @param credentials: tuple (логин, пароль)
        @param token: Токен для авторизации
        @raise IncorrectLogin: Если не найдено соответствия по логину
        @raise IncorrectPassword: Если соответствие по логину найдено, но хеши паролей не совпадают
        @return: Объект аутентифицированного пользователя

        """
        if credentials:
            return cls.authentificate_by_credentials(*credentials)
        elif token:
            return cls.authentificate_by_token(token)
        else:
            print("auth_data", credentials, token)
            raise NoDataForAuth()

    @classmethod
    def authentificate_by_request(cls, request: Request):
        """
        Выполняет аутентификацию пользователя по переданному объекту Request
        :param request: Запрос пользователя
        :return:
        """
        print("request-token", request.get("token", False))
        return cls.authentificate(
            (request.get("login"), request.get("password")) if request.get("login", False) else None,
            request.get("token", False)
        )

    @classmethod
    def authentificate_by_token(cls, token: str) -> Account:
        """
        Выполняет аутентификацию пользователя по переданному токену
        @param token: Токен для авторизации
        @raise IncorrectToken: Если не найдено соответствия по токену
        @return: Аккаунт пользователя

        """
        account_found = Accounts().get_item({"token": token})
        if account_found:
            return account_found
        else:
            raise IncorrectToken()

    @classmethod
    def authentificate_by_credentials(cls, login, password) -> Account:
        """
        Выполняет аутентификацию пользователя по переданным логину и паролю
        @param login: Логин
        @param password: Пароль
        @raise IncorrectLogin: Если не найдено соответствия по логину
        @raise IncorrectPassword: Если соответствие по логину найдено, но хеши паролей не совпадают
        @return: Аккаунт пользователя

        """
        account_found = Accounts().get_item({"login": login})
        if account_found:
            if account_found.password != md5(password):
                raise IncorrectPassword()
            return account_found
        else:
            raise IncorrectLogin()

    @classmethod
    def change_password(cls, login: str) -> str:
        """
        Меняет пароль аккаунта и возвращает новый

        @param login: Логин
        @return: Новый пароль
        """
        account = Accounts().get_item({"login": login})
        if not account:
            raise IncorrectLogin()
        account.set_new_token()
        new_passw = cls.gen_password()
        account.password = new_passw
        account.save()
        return new_passw

    @classmethod
    def set_new_password(cls, account, current_password: str, new_password: str, new_password2: str) -> str:
        """
        Меняет пароль аккаунта на новый
        @param account: Объект аккаунта пользователя
        @param current_password: Текущий пароль
        @param new_password: Новый пароль
        @param new_password2: Подтверждение нового пароля
        @return: Новый пароль
        """
        if not account:
            raise IncorrectLogin()
        if account.password != md5(current_password):
            raise IncorrectPassword()
        if new_password != new_password2:
            raise NewPasswordsMismatch()
        account.password = new_password
        account.save()
        return True

    @classmethod
    def send_email(cls, email, subject, html):
        message = MIMEText(html, "html", "utf-8")
        message['Subject'] = subject
        message['From'] = cls.smtp_config.emailfrom
        message['To'] = email
        message['Reply-To'] = cls.smtp_config.emailfrom
        conn = smtplib.SMTP_SSL(host=cls.smtp_config.emailsmtp[0], port=cls.smtp_config.emailsmtp[1])
        conn.login(cls.smtp_config.emailfrom, cls.smtp_config.emailpass)
        conn.sendmail(cls.smtp_config.emailfrom, email, message.as_string())
        conn.quit()
        return True

    @classmethod
    def send_sms(cls, phone, text, user, try_to_use_email=False, msg_type=None, host=None, paid_by=None):
        raise SmsError

    @classmethod
    def send_code(cls, email: str, code):
        return True

    @classmethod
    def send_email_confirmation_success(cls, email):
        return True

    @classmethod
    def gen_password(cls):
        """
        Генерирует читабельный пароль
        :return:
        """
        import random
        digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        symbols = ["!", "#", "@", "*", "%", "^", "&", "/", "\\"]
        characters = ["a", "b", "d", "e", "f", "g", "h", "j", "k", "m", "n",
                      "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z" ]
        digit1 = str(random.choice(digits))
        digit2 = str(random.choice(digits))
        upper_char = random.choice(characters).upper()
        random.shuffle(characters)
        random_start = random.choice([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
        random_end = random_start + 5
        chars = characters[random_start:random_end]
        l = [digit1, digit2, upper_char] + chars
        random.shuffle(l)
        return "".join(l)
