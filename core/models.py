import re
import unittest
from mapex import Pool, SqlMapper
from mapex import MySqlClient, MsSqlClient, PgSqlClient, MongoClient
from envi import Application as EnviApplication, ControllerMethodResponseWithTemplate
from suit.Suit import Suit, TemplateNotFound
from inspect import isabstract, isclass

from z9.core.utils import get_module_members

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
        self.map[Contours.BETA] = connection_tuples_map.get(Contours.BETA, self.map[Contours.PRODUCTION])
        self.map[Contours.UNITTESTS] = connection_tuples_map.get(Contours.UNITTESTS, self.map[Contours.BETA])

        self.pool = None
        self.init_pool(Contours.UNITTESTS)
        self.mappers = []
        for path in mappers_modules_paths:
            self.register_module(path)

    def init_pool(self, c: int):
        self.pool = Pool(self.adapter, self.map.get(c))

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


class UnitTest(unittest.TestCase):
    def __init__(self):
        super().__init__()

    def set_application(self, app: Application):
        app.contour = Contours.UNITTESTS
