
from datetime import datetime, timedelta
from envi import Application, Request, Controller, template

from z9.core.auth.models import AuthentificationService
from z9.core.auth.exceptions import NoDataForAuth, IncorrectToken

class AuthController(Controller):

    default_action = "login"

    @staticmethod
    def user_initialization_hook_static(app: Application, request: Request):
        """
        Стандартный алгоритм аутентификации
        :param app: Экземпляр приложения
        :param request: Запрос пользователя
        :return: Аккаунт пользователя
        """
        if request.path in ["/auth/login", "/auth/auth"]:
            return None
        auth_service = AuthentificationService()
        try:
            return auth_service.authentificate_by_request(request)
        except (NoDataForAuth, IncorrectToken):
            app.redirect("/auth/login/")

    @staticmethod
    @template("views.login")
    def login(request: Request, **kwargs):
        """ Страница с формой авторизации """
        request.response.set_cookie("token", "", path="/", expires=datetime.now() - timedelta(seconds=30*60))

    @staticmethod
    def auth(request: Request, **kwargs) -> bool:
        """ Выполняет аутентификацию и авторизацию пользователя

        @param request: Запрос пользователя
        @type request: Request
        @param kwargs: Параметры окружения
        @return: Результат выполнения авторизации
        @rtype : bool

        """
        auth_service = AuthentificationService()
        try:
            account = auth_service.authentificate_by_request(request)
            if account:
                request.response.set_cookie(
                    "token", account.set_new_token(), path="/", expires=datetime.now() + timedelta(seconds=30*60)
                )
                return {"redirect_to": "/"}
        except (NoDataForAuth, IncorrectToken) as err:
            request.response.set_cookie(
                "token", "", path="/", expires=datetime.now() - timedelta(seconds=30*60)
            )
            raise err

    @staticmethod
    def unauth(app: Application, request: Request, **kwargs) -> bool:
        """ Выполняет деаутентификацию

        @param request: Запрос пользователя
        @type request: Request
        @param kwargs: Параметры окружения
        @return: Результат выполнения авторизации
        @rtype : bool

        """
        request.response.set_cookie("token", "", path="/", expires=datetime.now() - timedelta(seconds=30*60))
        app.redirect("/")