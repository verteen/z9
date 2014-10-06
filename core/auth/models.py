
"""
Модели пакета sf.auth, отвечающие за аутентификационно-авторизационный слой системы

"""

import random
from datetime import datetime

from mapex import EntityModel, CollectionModel
from envi import Request
from z9.core.auth.mappers import AccountsMapper
from z9.core.auth.exceptions import *
from z9.core.utils import md5


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


class AuthentificationService(object):
    """ Сервис первичной аутентификации пользователей

    При удачной аутентификации сервис возвращает экземпляр аккаунта,
    под которым пользователь аутентифицирован

    """

    def __init__(self):
        self.accounts = Accounts()

    def authentificate(self, credentials: tuple=None, token: str=None) -> Account:
        """
        Выполняет аутентификацию пользователя по переданным данным
        @param credentials: tuple (логин, пароль)
        @param token: Токен для авторизации
        @raise IncorrectLogin: Если не найдено соответствия по логину
        @raise IncorrectPassword: Если соответствие по логину найдено, но хеши паролей не совпадают
        @return: Объект аутентифицированного пользователя

        """
        if credentials:
            return self.authentificate_by_credentials(*credentials)
        elif token:
            return self.authentificate_by_token(token)
        else:
            raise NoDataForAuth()

    def authentificate_by_request(self, request: Request):
        """
        Выполняет аутентификацию пользователя по переданному объекту Request
        :param request: Запрос пользователя
        :return:
        """
        return self.authentificate(
            (request.get("login"), request.get("password")) if request.get("login", False) else None,
            request.get("token", False)
        )

    def authentificate_by_token(self, token: str) -> Account:
        """
        Выполняет аутентификацию пользователя по переданному токену
        @param token: Токен для авторизации
        @raise IncorrectToken: Если не найдено соответствия по токену
        @return: Аккаунт пользователя

        """
        account_found = self.accounts.get_item({"token": token})
        if account_found:
            return account_found
        else:
            raise IncorrectToken()

    def authentificate_by_credentials(self, login, password) -> Account:
        """
        Выполняет аутентификацию пользователя по переданным логину и паролю
        @param login: Логин
        @param password: Пароль
        @raise IncorrectLogin: Если не найдено соответствия по логину
        @raise IncorrectPassword: Если соответствие по логину найдено, но хеши паролей не совпадают
        @return: Аккаунт пользователя

        """
        account_found = self.accounts.get_item({"login": login})
        if account_found:
            if account_found.password != md5(password):
                raise IncorrectPassword()
            return account_found
        else:
            raise IncorrectLogin()

    def change_password(self, login: str) -> str:
        """
        Меняет пароль аккаунта и возвращает новый

        @param login: Логин
        @return: Новый пароль
        """
        account = self.accounts.get_item({"login": login})
        if not account:
            raise IncorrectLogin()
        account.set_new_token()
        new_passw = self.gen_password()
        account.password = new_passw
        account.save()
        return new_passw

    @staticmethod
    def gen_password():
        """
        Генерирует читабельный пароль
        :return:
        """
        import random
        digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        symbols = ["!", "#", "@", "*", "%", "^", "&", "/", "\\"]
        characters = ["a", "b", "d", "e", "f", "g", "h", "j", "k", "m", "n",
                      "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z" ]
        digit = str(random.choice(digits))
        symbol = random.choice(symbols)
        upper_char = random.choice(characters).upper()
        random.shuffle(characters)
        random_start = random.choice([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
        random_end = random_start + 5
        chars = characters[random_start:random_end]
        l = [digit, symbol, upper_char] + chars
        random.shuffle(l)
        return "".join(l)
