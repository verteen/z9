""" Тестирование классов подсистемы авторизации

"""

from z9.core.models import EntityModelTest
from z9.core.auth.models import Account, Accounts, AuthentificationService
from z9.core.auth.exceptions import *


class AccountTests(EntityModelTest):
    """ Тестирование основных аспектов работы с учетными записями """

    model_for_test = Account

    def test_invalid_account(self):
        """ Чтобы новый аккаунт был добавлен он должен быть полностью сформирован """
        # Создадим экземпляр, но забудем указать логин
        account = Account()
        self.assertRaises(NoLoginForAccount, account.save)
        # Укажем логин, но забудем указать пароль
        account.login = "login"
        self.assertRaises(NoPasswordForAccount, account.save)
        # Укажем пароль, требуется тип аккаунта:
        account.password = "ewhuewds"
        account.validate()

    def test_dublicate_login(self):
        """ Нельзя добавить новый аккаунт, если указанный логин уже используется в системе """
        Account({"login": "login", "password": "sdsdsds"}).save()
        self.assertEqual(1, Accounts().count())

        account = Account({"login": "login", "password": "sdsdsds"})
        self.assertRaises(DublicateLogin, account.save)
        self.assertEqual(1, Accounts().count())

    def test_password_ecryption(self):
        """ При сохранении аккаунта пароль автоматически сохраняется в зашифрованном виде """
        Account({"login": "login", "password": "sdsdsds"}).save()

        account = Accounts().get_item({"login": "login"})
        self.assertEqual("837a502d6d0bb6e5c54b0204148eff40", account.password)

    def test_setting_tokens(self):
        """ Токен аккаунта меняется каждый раз, когда вызывается метод смены токена """
        account = Account({"login": "login", "password": "sdsdsds", "token": "123"}).save()
        new_token = account.set_new_token()
        account.refresh()
        self.assertNotEqual("123", account.token)
        self.assertEqual(new_token, account.token)


class AuthentificationServiceTests(EntityModelTest):
    """ Unit-тесты сервисы аутентификации и авторизации пользователей """

    model_for_test = Account

    def test_failed_authentification_not_enough_data(self):
        """ Аутентификация не проходит, если не получена необходимая для аутентификации информация """
        self.assertRaises(NoDataForAuth, AuthentificationService().authentificate)

    def test_failed_authentification_incorrect_login(self):
        """ Аутентификация не проходит, если указан некорректный логин """
        Account({"login": "login", "password": "pass"}).save()
        self.assertRaises(IncorrectLogin, AuthentificationService().authentificate, credentials=("blabla", "pass"))

    def test_failed_authentification_incorrect_password(self):
        """ Аутентификация не проходит, если указан некорректный пароль """
        Account({"login": "login", "password": "12345"}).save()
        self.assertRaises(IncorrectPassword, AuthentificationService().authentificate, credentials=("login", "pass"))

    def test_success_authentification_by_login_and_password(self):
        """ Аутентификация проходит, если указаны корректные логин и пароль, принадлежащие одному из пользователей """
        Account({"login": "login", "password": "12345"}).save()
        authentificated_account = AuthentificationService().authentificate(credentials=("login", "12345"))
        self.assertTrue(isinstance(authentificated_account, Account))

    def test_failed_authentification_incorrect_token(self):
        """ Аутентификация не проходит, если указан некорректный токен """
        Account({"login": "login", "password": "12345", "token": "12345678"}).save()
        self.assertRaises(IncorrectToken, AuthentificationService().authentificate, token="zxcvbn")

    def test_success_authentification_by_token(self):
        """ Аутентификация проходит, если указан корректный токен, принадлежащий одному из пользователей """
        Account({"login": "login", "password": "12345", "token": "12345678"}).save()
        authentificated_account = AuthentificationService().authentificate(token="12345678")
        self.assertTrue(isinstance(authentificated_account, Account))