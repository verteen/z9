import random
from datetime import datetime, timedelta
from envi import Application, Request, Controller, template

from z9.core.models import Phone
from z9.core.auth.models import AuthentificationService, Account, Accounts
from z9.core.auth.exceptions import *


class AuthController(Controller):

    default_action = "login"
    auth_service = lambda: None
    users_collection = lambda: None
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
            a = cls.auth_service().authentificate_by_request(request)
            return a
        except (NoDataForAuth, IncorrectToken):
            if auto_register:
                return cls.new_default_account(request, auto_register=auto_register)
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
    def new_default_account(cls, request: Request, do_auth=True, auto_register=False) -> Account:
        account = Account({"login": AuthentificationService.gen_password(), "password": AuthentificationService.gen_password()})
        if do_auth:
            request.set("token", account.set_new_token())
            cls.auth(request)
        if auto_register:
            cls.users_collection().get_new_item().load_from_array({"name": "user", "account": account}).save()
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
                    "token", account.set_new_token() if not request.get("use_prev_token", False) else account.token,
                    path="/", expires=datetime.now() + timedelta(seconds=30*60)
                )
                return {"redirect_to": cls.root} if not request.get("use_prev_token", False) else True
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

    @classmethod
    def ajax_auth(cls, user, request: Request, **kwargs):
        request.set("login", Phone(request.get("login")).get_value())
        if AuthController.auth(request, **kwargs):
            return {
                "user": user.stringify(["position_name", "name", "phone", "phone_verified", "email", "email_verified"]),
                "preview_randomizer": datetime.now().microsecond
            }

    @classmethod
    def check_phone_registration(cls, user, request: Request, **kwargs):
        phone = Phone(request.get("phone")).get_value()
        target_user = cls.users_collection().get_item({"account.login": phone, "phone_verified": True})
        if target_user:
            return {"email_verified": target_user.email_verified, "phone_verified": target_user.phone_verified}
        else:
            raise NotRegisteredYet()

    @classmethod
    def fast_registration_stage1(cls, user, request: Request, **kwargs):
        if user.phone_verified:
            raise AlreadyRegistred()

        phone = Phone(request.get("phone")).get_value()
        if cls.users_collection().count({"account.login": phone, "phone_verified": True}):
            raise AlreadyRegistred()

        account = Accounts().get_item({"login": user.account.login})
        account.login = phone
        account.save()
        user.account = account
        user.verification_code = "%d%d%d%d" % (
            random.choice(range(9)), random.choice(range(9)), random.choice(range(9)), random.choice(range(9))
        )
        user.save()
        #r = SMSC().send_sms(phone.replace("+", ""), "REPAEM.RU\nКод подтверждения: %s" % user.verification_code, sender="repaem.ru")
        r = True
        if r:
            return user.verification_code
        raise SmsError()

    @classmethod
    def fast_registration_stage2(cls, user, request: Request, **kwargs):
        if not user.verification_code:
            user.phone_verified = False
            user.verification_code = None
            user.verification_code_failed_attempts = 0
            user.save()
            raise IncorrectVerificationCodeFatal()

        if user.verification_code == request.get("verification_code"):
            user.phone_verified = True
            user.verification_code = None
            user.verification_code_failed_attempts = 0
            user.save()
            return {
                "user": user.stringify(["position_name", "name", "phone", "phone_verified", "email", "email_verified"]),
                "preview_randomizer": datetime.now().microsecond
            }
        else:
            user.verification_code_failed_attempts += 1
            if user.verification_code_failed_attempts < 3:
                user.save()
                raise IncorrectVerificationCode()
            else:
                user.phone = None
                user.phone_verified = False
                user.verification_code = None
                user.verification_code_failed_attempts = 0
                user.save()
                raise IncorrectVerificationCodeFatal()

    @classmethod
    def send_recovery_codes(cls, user, request: Request, **kwargs):
        phone = Phone(request.get("phone")).get_value()

        target_user = cls.users_collection().get_item({"account.login": phone, "phone_verified": True})
        if not target_user:
            raise NotRegisteredYet()

        if target_user.email_verified:
            raise EmailIsVerified()

        target_user.email = request.get("email")
        target_user.verification_code = "%d%d%d%d" % (
            random.choice(range(9)), random.choice(range(9)), random.choice(range(9)), random.choice(range(9))
        )
        target_user.verification_code2 = "%d%d%d%d" % (
            random.choice(range(9)), random.choice(range(9)), random.choice(range(9)), random.choice(range(9))
        )
        target_user.save()
        #r = SMSC().send_sms(phone.replace("+", ""), "REPAEM.RU\nКод подтверждения: %s" % target_user.verification_code, sender="repaem.ru")
        r = True
        cls.auth_service().send_code(target_user.email, target_user.verification_code2)
        if r:
            return target_user.verification_code, target_user.verification_code2
        else:
            raise SmsError()

    @classmethod
    def recover_password(cls, user, request: Request, **kwargs):
        phone = Phone(request.get("phone")).get_value()
        target_user = cls.users_collection().get_item({"account.login": phone, "phone_verified": True})
        if target_user.email_verified:
            cls.auth_service().change_password(target_user.email)
            return True
        if target_user.verification_code == request.get("vc1") and target_user.verification_code2 == request.get("vc2"):
            target_user.email_verified = True
            target_user.verification_code = None
            target_user.verification_code_failed_attempts = 0
            target_user.save()
            cls.auth_service().change_password(target_user.email)
            return True
        else:
            target_user.verification_code_failed_attempts += 1
            if target_user.verification_code_failed_attempts < 3:
                target_user.save()
                raise IncorrectVerificationCode()
            else:
                target_user.email = None
                target_user.email_verified = False
                target_user.verification_code = None
                target_user.verification_code2 = None
                target_user.verification_code_failed_attempts = 0
                target_user.save()
                raise IncorrectVerificationCodeFatal()

    @classmethod
    def confirm_email_and_auth(cls, user, request: Request, **kwargs):
        phone = Phone(request.get("phone")).get_value()
        target_user = cls.users_collection().get_item({"account.login": phone, "phone_verified": True})
        if target_user.verification_code == request.get("vc1") and target_user.verification_code2 == request.get("vc2"):
            target_user.email_verified = True
            target_user.verification_code = None
            target_user.verification_code_failed_attempts = 0
            target_user.save()
            user.refresh()
            return {
                "user": user.stringify(["position_name", "name", "phone", "phone_verified", "email", "email_verified"]),
                "preview_randomizer": datetime.now().microsecond
            }
        else:
            target_user.verification_code_failed_attempts += 1
            if target_user.verification_code_failed_attempts < 3:
                target_user.save()
                raise IncorrectVerificationCode()
            else:
                target_user.email = None
                target_user.email_verified = False
                target_user.verification_code = None
                target_user.verification_code2 = None
                target_user.verification_code_failed_attempts = 0
                target_user.save()
                raise IncorrectVerificationCodeFatal()
