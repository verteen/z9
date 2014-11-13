import re
import unittest
from mapex import Pool, SqlMapper, EntityModel, EmbeddedObject
from mapex import MySqlClient, MsSqlClient, PgSqlClient, MongoClient
from envi import Application as EnviApplication, ControllerMethodResponseWithTemplate
from suit.Suit import Suit, TemplateNotFound
from inspect import isabstract, isclass

from z9.core.utils import get_module_members
from z9.core.exceptions import InvalidPhoneNumber


class Application(EnviApplication):
    """ Стандартное приложение z9 """

    def __init__(self):
        super().__init__()
        self._databases = []
        self._contour = None
        self.contour = Contours.UNITTESTS

    def database(self, d):
        d.switch(self.contour)
        self._databases.append(d)

    @property
    def contour(self):
        return self._contour

    @contour.setter
    def contour(self, c: int):
        self._contour = c
        for db in self._databases:
            db.switch(c)

    def start_testing(self):
        self.contour = Contours.UNITTESTS

    def start_production(self):
        self.contour = Contours.PRODUCTION

    def start_beta(self):
        self.contour = Contours.BETA

    def ajax_output_converter(self, result) -> dict:
        """ Функция для конвертации ответов при ajax запросах
        Настраиваем формат положительных и отрицательных результатов ajax-запросов
        :param result: Экземпляр исключения (Exception) или Словарь с данными (dict)
        """
        if isinstance(result, Exception):
            exc = result
            match = re.search("'(.+)'", str(exc.__class__))
            err_type = match.group(1) if match else exc.__class__.__name__
            result = {"error": {"type": err_type, "message": str(exc), "data": {}}}
            return result
        else:
            return {"result": result}

    def static_output_converter(self, result: ControllerMethodResponseWithTemplate) -> str:
        """ Функция для конвертации ответов при статических загрузках страницы
        Подключаем Suit в качестве кастомной шаблонизации
        :param result: Ответ в формате ControllerMethodResponseWithTemplate
        """
        # noinspection PyBroadException
        try:
            return Suit(result.template).execute(result.data)
        except TemplateNotFound:
            return str(result)


class Contours(object):
    PRODUCTION = 9
    BETA = 5
    UNITTESTS = 0


class DbClients(object):
    MYSQL = MySqlClient
    PGSQL = PgSqlClient
    MSSQL = MsSqlClient
    MONGO = MongoClient


class Database(object):
    def __init__(self, adapter, mappers_modules_paths: list, connection_tuples_map: dict):
        self.adapter = adapter
        # noinspection PyDictCreation
        self.map = {}
        self.map[Contours.PRODUCTION] = connection_tuples_map.get(Contours.PRODUCTION)
        self.map[Contours.BETA] = connection_tuples_map.get(Contours.BETA)
        self.map[Contours.UNITTESTS] = connection_tuples_map.get(Contours.UNITTESTS)

        self.pool = None
        self.init_pool(Contours.UNITTESTS)
        self.mappers = []
        for path in mappers_modules_paths:
            self.register_module(path)

    def init_pool(self, c: int):
        self.pool = Pool(self.adapter, self.map.get(c), min_connections=10)

    def register_mapper(self, mapper: SqlMapper):
        mapper.pool = self.pool
        self.mappers.append(mapper)

    def register_module(self, *args):
        for mapper in get_module_members(
                *args, predicate=lambda c: isclass(c) and issubclass(c, SqlMapper) and not isabstract(c)
        ):
            self.register_mapper(mapper)

    def switch(self, c: int):
        self.init_pool(c)
        for mapper in self.mappers:
            mapper.pool = self.pool


class EntityModelTest(unittest.TestCase):
    model_for_test = EntityModel

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        self.model_for_test().get_new_collection().delete()


class Phone(EmbeddedObject):
    """ Класс для представления телефонных номеров """
    value_type = str

    def __init__(self, number, default_if_error=False):
        self._digits = re.sub("[^\d]", "", str(number))
        self._default_if_error = default_if_error
        self._validate()

    def __str__(self):
        v = self._normalize()
        return v if v else ""

    def _normalize(self) -> str:
        """ Приводит номер к правильному строковому представлению """
        return "+7%s" % (
            self._digits[1 if self._digits[0] in ["7", "8"] else 0:11]
        ) if len(self._digits) >= 10 else self._default_if_error

    def get_value(self) -> str:
        """ Возвращает обозначение пола клиента для базы данных """
        v = self._normalize()
        return v if v else ""

    def _validate(self):
        """
        Проверяет корректность указания номера телефона
        @return: Телефонный номер, приведенный к единому формату
        @raise InvalidPhoneNumber: Если переданный номер некорректен и его невозможно отформатировать

        """
        if len(self._digits) < 10 and self._default_if_error is False:
            raise InvalidPhoneNumber(self._normalize())