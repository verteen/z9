""" Тестирование моделей UI """
from unittest import TestCase

from z9.core.web.models import Menu, MenuItem


class MenuTest(TestCase):
    """  """
    def setUp(self):
        contracts = MenuItem("/contracts/", "Система ввода договоров", sub_menu=Menu([
            MenuItem("/contracts/new/", "Новый договор", css_class="bold italic"),
            MenuItem("/contracts/show/", "Список договоров")
        ]))

        profile = MenuItem("/profile/", "Профиль", sub_menu=Menu([
            MenuItem("/profile/show/", "Личные данные"),
            MenuItem("/profile/password/", "Сменить пароль"),
            MenuItem("/profile/avatar/", "Установить аватар"),
        ]))

        exit_link = MenuItem("/exit/", "Выход")

        self.menu = Menu([contracts, profile, exit_link])

    def test_get_full_menu_as_dict(self):
        """ Объект меню возвращает все меню в виде словаря """

        expected = [
            {"url": "/contracts/", "alias": "Система ввода договоров", "css_class": "", "active": False, "childs": [
                {"url": "/contracts/new/", "alias": "Новый договор", "css_class": "bold italic", "childs": [], "active": False},
                {"url": "/contracts/show/", "alias": "Список договоров", "css_class": "", "childs": [], "active": False}
            ]},
            {"url": "/profile/", "alias": "Профиль", "css_class": "", "active": False, "childs": [
                {"url": "/profile/show/", "alias": "Личные данные", "css_class": "", "childs": [], "active": False},
                {"url": "/profile/password/", "alias": "Сменить пароль", "css_class": "", "childs": [], "active": False},
                {"url": "/profile/avatar/", "alias": "Установить аватар", "css_class": "", "childs": [], "active": False}
            ]},
            {"url": "/exit/", "alias": "Выход", "css_class": "", "childs": [], "active": False}
        ]

        self.assertCountEqual(expected, self.menu.get_full())

    def test_get_submenu(self):
        """ Объект меню может вернуть подменю по переданному URL """

        expected = [
            {"url": "/profile/show/", "alias": "Личные данные", "css_class": "", "childs": [], "active": False},
            {"url": "/profile/password/", "alias": "Сменить пароль", "css_class": "", "childs": [], "active": False},
            {"url": "/profile/avatar/", "alias": "Установить аватар", "css_class": "", "childs": [], "active": False}
        ]
        self.assertCountEqual(expected, self.menu.get_sub_menu("/profile/").get_full())

    def test_active_menu(self):
        """ Объект меню знает активный он или нет """
        expected = [
            {"url": "/profile/show/", "alias": "Личные данные", "css_class": "", "childs": [], "active": True},
            {"url": "/profile/password/", "alias": "Сменить пароль", "css_class": "", "childs": [], "active": False},
            {"url": "/profile/avatar/", "alias": "Установить аватар", "css_class": "", "childs": [], "active": False}
        ]
        self.assertCountEqual(expected, self.menu.get_sub_menu("/profile/").get_full(url='/profile/show/'))


    def test_get_breadcrumbs(self):
        """ Объект меню может вернуть хлебные крошки по переданному URL """
        empty = []
        breadcrumbs = [
            {"url": "/profile/", "alias": "Профиль"},
            {"alias": "Сменить пароль"}
        ]
        self.assertCountEqual(empty, self.menu.get_breadcrumbs("/"))
        self.assertCountEqual(empty, self.menu.get_breadcrumbs("/blablabla/sdsds/"))
        self.assertCountEqual(empty, self.menu.get_breadcrumbs("/profile/"))
        self.assertCountEqual(breadcrumbs, self.menu.get_breadcrumbs("/profile/password/"))

    def test_get_data(self):
        """ Объект меню возвращает словарь, содеражащий все эелемент меню """
        self.assertCountEqual(["breadcrumbs", "main_menu", "sub_menu"], self.menu.get_data("doesn't matter"))