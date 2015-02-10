""" Модели для веб разработки """
from mapex import CollectionModel
from collections import OrderedDict
from envi import Request
from z9.core.exceptions import CommonException


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

    def get_data(self, url=None) -> dict:
        """ Возвращает описание пункта меню в виде словаря """
        return {
            "url": self.url,
            "alias": self.alias,
            "css_class": self.css_class,
            "childs": self.sub_menu.get_full(),
            "active": self.url == url
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

    def get_full(self, url=None) -> list:
        """ Возвращает структуру меню в виде списка словарей """
        return [item.get_data(url) for item in self.items]

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
            "main_menu": self.get_full(url),
            "sub_menu": self.get_sub_menu(url).get_full(url),
            "breadcrumbs": self.get_breadcrumbs(url)
        }


class TableView(CollectionModel):
    """ Класс для представления коллекции в виде структуры данных пригодной для использования в шаблонизаторе """
    template = ""
    header = []
    properties = []
    boundaries = {}
    params = {}

    record_exists_exception = CommonException("Row exists already")
    record_not_found_exception = CommonException("Row not found")

    def __init__(self, *boundaries, **kwargs):
        super().__init__(*boundaries, **kwargs)
        self._orders = {}
        for prop in self.properties:
            self._orders.update({'{prop}-asc'.format(prop=prop): (prop, 'ASC')})
            self._orders.update({'{prop}-desc'.format(prop=prop): (prop, 'DESC')})

        for bounds in boundaries:
            self.boundaries.update(bounds)

    def rows(self, sort):
        """ Возвращает строки таблицы
        :return:
        """
        params = self.params.copy()
        if sort:
            params.update({'order': self._orders.get(sort)})

        rows = OrderedDict()
        for item in self.get_items(self.boundaries, params=params):
            rows[item.primary.value] = item.stringify(self.properties)
        return rows

    def set_sub_boundaries(self, sub_boundaries: dict):
        """ Устанавливаеь дополнительные ограничения на таблицу (Что-то вроде фильтра или поиска по таблице)
        :param sub_boundaries: Дополнительные условия выборки записей
        """
        self.boundaries.update(sub_boundaries)

    def represent(self, request: Request=None):
        """ Возвращает коллекцию в виде пригодном для шаблонизатора """

        sort = request.get('sort', None)\
            if request.get('sort', None) in self._orders\
            else None

        return {"template": self.template, "header": self.header, "rows": self.rows(sort), "sort": sort}

    def create(self, request: Request):
        """ Создание новой записи если её ещё не существует """
        data = dict(request.items())

        model = self.get_new_item(data)
        if model.mapper.primary.exists() and self.count(model.primary.to_dict()):
            raise self.record_exists_exception
        model.save()

    # noinspection PyMethodOverriding
    def update(self, request: Request):
        """ Обновление записи если она существует """
        data = dict(request.items())
        data_model = self.get_new_item(data)
        model = self.get_item(data_model.primary.to_dict())
        if model is None:
            raise self.record_not_found_exception
        model.load_from_array(data).save()

    # noinspection PyMethodOverriding
    def delete(self, request: Request):
        """ Удаление нескольких записей """
        pkeys = request.get(self.mapper.primary.name())
        if not isinstance(pkeys, list):
            pkeys = [pkeys]
        super().delete({self.mapper.primary.name(): ("in", pkeys)})
