
from datetime import datetime, timedelta
from envi import Application, Request, Controller, template

from z9.core.auth.models import AuthentificationService, Account
from z9.core.auth.exceptions import NoDataForAuth, IncorrectToken


class AuthController(Controller):

    default_action = "login"
    auth_service = AuthentificationService
    root = "/"

    @classmethod
    def user_initialization_hook_static(cls, app: Application, request: Request, auto_register=None):
        """
        Стандартный алгоритм аутентификации
        :param app: Экземпляр приложения
        :param request: Запрос пользователя
        :return: Аккаунт пользователя
        """
        if request.path in [
            "{}auth/login".format(cls.root),
            "{}auth/auth".format(cls.root),
            "{}auth/change_password".format(cls.root),
        ]:
            return None

        try:
            return cls.auth_service().authentificate_by_request(request)
        except (NoDataForAuth, IncorrectToken):
            if auto_register:
                return cls.new_default_account(request)
            else:
                app.redirect("{}auth/login/".format(cls.root))

    @classmethod
    def user_initialization_hook(cls, request: Request):
        """
        Стандартный алгоритм аутентификации
        :param request: Запрос пользователя
        :return: Аккаунт пользователя
        """
        if request.path in [
            "{}auth/login".format(cls.root),
            "{}auth/auth".format(cls.root),
            "{}auth/change_password".format(cls.root),
            ]:
            return None
        return cls.auth_service().authentificate_by_request(request)

    @classmethod
    def new_default_account(cls, request: Request) -> Account:
        account = Account({"login": AuthentificationService.gen_password(), "password": AuthentificationService.gen_password()})
        request.set("token", account.set_new_token())
        cls.auth(request)
        return account

    @staticmethod
    @template("views.login")
    def login(request: Request, **kwargs):
        """ Страница с формой авторизации """
        request.response.set_cookie("token", "", path="/", expires=datetime.now() - timedelta(seconds=30*60))

    @classmethod
    def auth(cls, request: Request, **kwargs) -> bool:
        """ Выполняет аутентификацию и авторизацию пользователя

        @param request: Запрос пользователя
        @type request: Request
        @param kwargs: Параметры окружения
        @return: Результат выполнения авторизации
        @rtype : bool

        """
        try:
            account = cls.auth_service().authentificate_by_request(request)
            if account:
                request.response.set_cookie(
                    "token", account.set_new_token(), path="/", expires=datetime.now() + timedelta(seconds=30*60)
                )
                return {"redirect_to": cls.root}
        except (NoDataForAuth, IncorrectToken) as err:
            request.response.set_cookie(
                "token", "", path="/", expires=datetime.now() - timedelta(seconds=30*60)
            )
            raise err

    @classmethod
    def unauth(cls, app: Application, request: Request, **kwargs) -> bool:
        """ Выполняет деаутентификацию

        @param request: Запрос пользователя
        @type request: Request
        @param kwargs: Параметры окружения
        @return: Результат выполнения авторизации
        @rtype : bool

        """
        request.response.set_cookie("token", "", path="/", expires=datetime.now() - timedelta(seconds=30*60))
        app.redirect(cls.root)

    @classmethod
    def change_password(cls, request: Request, **kwargs):
        """ Меняет пароль аккаунта на новый

        @param request:
        @param kwargs:
        @return:
        """
        return cls.auth_service().change_password(request.get("login"))
