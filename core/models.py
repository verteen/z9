import re
import unittest
from mapex import Pool, SqlMapper, EntityModel
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


class EntityModelTest(unittest.TestCase):
    model_for_test = EntityModel

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        self.model_for_test().get_new_collection().delete()


class CommonException(Exception):
    """ Базовый тип исключений """
    message = ""

    def __init__(self, data=None):
        super().__init__(self.message)
        self.data = data or {}

    @classmethod
    def name(cls) -> str:
        """ Возвращает полное имя исключения
        @return:
        """
        match = re.search("'(.+)'", str(cls))
        return match.group(1) if match else cls.__name__


class MenuItem(object):
    """
    Элемент меню
    :param url: URL элемента меню
    :param alias: Имя пункта меню
    :param css_class: css-класс пункта меню
    :param sub_menu: Подменю
    """

    def __init__(self, url: str, alias: str, css_class=None, sub_menu=None):
        self.url = url
        self.alias = alias
        self.css_class = css_class if css_class else ""
        self.url_map = {self.url: self}
        self.parent = Menu()
        self.sub_menu = sub_menu if sub_menu else Menu()
        self.sub_menu.parent = self

    def append(self, items):
        """
        Добавляет новые элементы в текущий пункт меню
        :param items: Список дочерних пунктов меню
        """
        self.sub_menu.append(items)
        self.url_map.update(self.sub_menu.items_map)

    def get_data(self) -> dict:
        """ Возвращает описание пункта меню в виде словаря """
        return {
            "url": self.url,
            "alias": self.alias,
            "css_class": self.css_class,
            "childs": self.sub_menu.get_full()
        }

    @property
    def breadcrumbs(self) -> list:
        """ Хлебные крошки для текущего пункта меню """
        return self.parent.breadcrumbs + [{"url": self.url, "alias": self.alias}]


class Menu(object):
    """ Меню """
    def __init__(self, items: list=None):
        self.parent = None
        self.items = []
        self.items_map = {}
        if items:
            self.append(items)

    def append(self, items):
        """
        Добавляет новый пункт в меню
        :param items: Список пунктов меню для добавления
        """
        self.items.extend(items)
        for item in items:
            item.parent = self
            self.items_map.update(item.url_map)
            self.items_map.update(item.sub_menu.items_map)

    def get_full(self) -> list:
        """ Возвращает структуру меню в виде списка словарей """
        return [item.get_data() for item in self.items]

    def get_sub_menu(self, url: str):
        """
        Возвращает подменю для указанного URL
        :param url: URL элемента меню, для которого необходимо вернуть подменю
        :return:
        """
        menu_item = self.items_map.get(url, None)
        return menu_item.sub_menu if menu_item else Menu()

    @property
    def breadcrumbs(self) -> list:
        """ Хлебные крошки для текущего пункта меню """
        return self.parent.breadcrumbs if self.parent else []

    def get_breadcrumbs(self, url: str):
        """
         Возвращает хлебные крошки для указанного URL
         :param url: URL элемента меню, для которого необходимо вернуть хлебные крошки
         :return:
         """
        menu_item = self.items_map.get(url, None)
        menu_item_parent_bc = menu_item.parent.breadcrumbs if menu_item else []
        return (menu_item_parent_bc + [{"alias": menu_item.alias}]) if menu_item_parent_bc else []

    def get_data(self, url: str) -> dict:
        """
        Возвращает все данные из объекта меню
        :param url: URL текущего положения
        :return:
        """
        return {
            "main_menu": self.get_full(),
            "sub_menu": self.get_sub_menu(url).get_full(),
            "breadcrumbs": self.get_breadcrumbs(url)
        }