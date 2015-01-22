""" Вспомогательные утитилиты """

import re
import os
import hashlib
import unittest
import webtest
import json
from itertools import filterfalse, chain
from importlib import import_module
from inspect import getmembers
from fcntl import flock, LOCK_EX, LOCK_NB

from z9.core.exceptions import CommonException


root_path = "%s/../" % os.path.dirname(os.path.abspath(__file__))


def md5(string):
    """ Возвращает md5 от строки
    :param string: Строка для кодирования
    :return: Результат хэширования
    """
    if not isinstance(string, bytes):
        string = str(string).encode()
    return hashlib.md5(string).hexdigest()


def partition(predicate, iterable):
    """
    Разбивает iterable на два по условию выполнения функции predicate
    @param predicate: Предикат, принимающий значение из iterable
    @param iterable: Итерируемая коллекция
    @return: Последовательность из двух генераторов (Значения удовлетворяющие предикату, не удовлетворяющие)
    """
    predicate = bool if predicate is None else predicate
    return filter(predicate, iterable), filterfalse(predicate, iterable)


def try_except(cb, exc_map):
    """
    Выполняет выражение cb и в случае возникновения исключения,
    описанного в exc_map, возвращает соответствующее этому исключению значение
    @param cb: Исполняемое выражение
    @param exc_map: Словарь соответствий отслеживаемых исключений и возвращаемых значений
    @return: Результирующее значение
    @raise Exception: Если возникшее
    """
    try:
        return cb()
    except Exception as err:
        for exc in exc_map:
            if isinstance(err, exc):
                return exc_map[exc]
        raise err


def trim_spaces(string):
    """ Удаляет переносы строк, табуляцию и дублирующиеся пробелы
    @param string: Строка для удаления переноса строк
    """
    string = string.replace("\t", "  ").replace("\n", "  ").replace("\r", "  ")
    string = re.sub("\s\s+", " ", string, flags=re.MULTILINE)
    string = string.strip(" ")
    return string


def chunked(l: list, size: int) -> [[]]:
    """ Возвращает список, разбитый на несколько списков заданного размера
    @param l: исходный список
    @param size: желаемый размер списков
    """
    return [l[:size]] + chunked(l[size:], size) if len(l) else []


def get_module_members(*args, predicate=None) -> list:
    """ Возвращает все части модуля удовлетворяющие условию predicate
    @param args: список модулей в которых проводится поиск
    @param predicate: условие поиска
    """
    modules = (import_module(module) if isinstance(module, str) else module for module in args)
    modules_members = map(lambda module: getmembers(module, predicate), modules)
    return [value for name, value in chain(*list(modules_members))]


def get_class_name(cls) -> str:
    """ Возвращает полное имя класса
    @param cls: класс
    @return:
    """
    match = re.search("'(.+)'", str(cls))
    return match.group(1) if match else cls.__name__

def get_class(path):
    """
    Возвращает класс по полному пути до него (как используется при импорте)
    @return:
    """
    path = path.split(".")
    spec_class = path.pop()
    module = ".".join(path)
    module = import_module(module)
    options = list(filter(lambda c: c == spec_class, module.__dir__()))
    candidate = getattr(module, options[0]) if len(options) > 0 else None
    return candidate

def with_lock(lock_name, cb):
    """
    Вычисляет выражение cb при успешной попытке блокирования доступа к файлу lock_name
    @param lock_name: имя файла блокировки
    @param cb: лямбда для получения результата
    """
    if os.path.exists(lock_name) and os.path.getsize(lock_name) > 0:
        raise Exception("Lockfile '%s' is not empty!" % lock_name)

    with open(lock_name, "w") as f:
        try:
            flock(f, LOCK_EX | LOCK_NB)
        except IOError:
            return

        return cb()


class FunctionalTestCase(unittest.TestCase):
    """ Класс для создания функциональных тестов """
    application=None

    def setUp(self):
        super().setUp()
        self.app = webtest.TestApp(self.application)
        self.maxDiff = None

    def xhr_query(self, url: str, data: dict=None, auth_token: str=None):
        """ Выполняет запрос к приложению методом POST, используя для авторизации переданный токен
        :param url: URL для запроса
        :param data: Данные для запроса
        :param auth_token: Токен для авторизации
        :return:
        """
        data = data if data else {}
        data.update({"token": auth_token})
        response = self.app.post(url, {"json": json.dumps(data)}, xhr=True)
        self.assertEqual("200 OK", response.status)
        return response.body

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def assertResponseEqual(self, expected, value):
        """
        Проверяет, совпадают ли переданные значения в бинарном представлении
        @param expected: Ожидаемое значение
        @param value: Проверяемое значение
        @raise AssertionError: Если значения не совпадают
        """
        if type(expected) is dict:
            self.assertDictEqual(expected, json.loads(value.decode()))
        else:
            self.assertEqual(expected, json.loads(value.decode()))

    def from_json(self, response_text):
        """ Конвертирует ответ сервера из json'a
        Просто для удобства
        @param response_text:
        @return:
        """
        return json.loads(response_text.decode())

    # noinspection PyPep8Naming
    def assertResponseRaises(self, excClass, response, custom_message=None):
        """ Проверяет что в ответе есть исключение
        @param excClass: Ожидаемое исключение
        @param response: Тело ответа
        """
        force_class_name = str(excClass).replace("<class '", "").replace("'>", "")
        response = json.loads(response.decode())
        self.assertEqual(
            excClass.name() if issubclass(excClass, CommonException) else force_class_name,
            response.get("error", {}).get("type", response)
        )

    # noinspection PyPep8Naming
    def assertResponseCookiesContains(self, response, cookie: str, value: str=None) -> bool:
        """
        Проверяет, есть ли в заголовках ответа установка cookie с указанным именем key и значением value (если указано)
        @param cookie: Имя cookie
        @param value: Значение cookie (Опционально)
        @return:
        """
        cookies = {}
        for header in response.headers:
            header_key, header_value = header, response.headers[header]
            if header_key == 'Set-Cookie':
                cookie_name, cookie_value, *junk = header_value.split("=")
                cookies[cookie_name] = cookie_value
        self.assertIn(cookie, cookies)
        if value:
            self.assertEqual(value, cookies.get(cookie))