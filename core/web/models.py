""" Модели для веб разработки """
from mapex import CollectionModel
from collections import OrderedDict


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


class TableView(CollectionModel):
    """ Класс для представления коллекции в виде структуры данных пригодной для использования в шаблонизаторе """
    def __init__(self, *boundaries):
        super().__init__(*boundaries)
        self.template = ""
        self.caption = ""
        self.header = []
        self.properties = []
        self._rows = None
        self.boundaries = {}
        for bounds in boundaries:
            self.boundaries.update(bounds)
        self.primary_extracter = lambda rm: rm

    @property
    def rows(self):
        """ Возвращает строки таблицы
        :return:
        """
        if self._rows is None:
            self._rows = {
                self.primary_extracter(it): self.ordered({
                    p: str(it.fetch(p)) for p in self.properties
                }, self.properties) for it in self.get_items(self.boundaries)
            }
        return self._rows

    @staticmethod
    def ordered(unordered: dict, order_keys: list) -> dict:
        """ Возвращает копию словаря, отсортированную в соответствии со списком ключей
        :param unordered: Словарь для сортировки
        :param order_keys: Список ключей
        :return: Отсортированный словарь
        """
        ordered = OrderedDict()
        for key in order_keys:
            ordered[key] = unordered.get(key)
        return ordered

    @rows.setter
    def rows(self, rows: dict):
        """ Заполняет объект таблицы указанными строками
        :param rows: Строки таблицы в виде словаря {id_строки: {"поле": "значение"}}
        """
        self._rows = rows

    def set_caption(self, caption: str):
        """ Устанавливает заголовок таблицы
        :param caption: Заголовок для таблицы
        :return:
        """
        self.caption = caption

    def set_sub_boundaries(self, sub_boundaries: dict):
        """ Устанавливаеь дополнительные ограничения на таблицу (Что-то вроде фильтра или поиска по таблице)
        :param sub_boundaries: Дополнительные условия выборки записей
        """
        self.boundaries.update(sub_boundaries)

    def represent(self):
        """ Возвращает коллекцию в виде пригодном для шаблонизатора """
        return {"template": self.template, "caption": self.caption, "header": self.header, "rows": self.rows}
