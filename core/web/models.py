""" Модели для веб разработки """
from mapex import EntityModel, CollectionModel, EmbeddedObject
from collections import OrderedDict
from envi import Request
from z9.core.exceptions import CommonException
from math import ceil
from z9.core.utils import pretty_print


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
            "active": url.startswith(self.url)
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


class Pager(object):
    @property
    def limit(self):
        return self._limit

    @property
    def offset(self):
        return (self._page - 1) * self._limit

    def range(self, a, b):
        return list(range(a, b + 1))

    def __init__(self, collection: CollectionModel, request: Request):
        self._page = None
        self._pages = []
        self._pages_count = None

        self._limit = None
        self._limits = []

        items_count = collection.count(collection.boundaries)

        # Допустимые значения для лимита
        for limit in [10, 30, 100]:
            if items_count > limit:
                self._limits.append(limit)

        try:
            self._limit = int(request.get("limit", 10))
            if self._limit not in self._limits:
                self._limit = 10
        except ValueError:
            self._limit = 10

        try:
            self._page = int(request.get("page", 1))
        except ValueError:
            self._page = 1

        self._pages_count = ceil(items_count / self._limit)

        if self._page < 1:
            self._page = 1

        if 0 < self._pages_count < self._page:
            self._page = self._pages_count

        self.pages_factory()

    def pages_factory(self):
        if self._pages_count > 10:
            a = max(self._page - 2, 1)
            b = max(self._page + 3, 6)
            c = self._pages_count - 4
            d = self._pages_count + 1

            if d - a > 10:
                self._pages = list(range(a, b)) + ['...'] + list(range(c, d))
            else:
                self._pages = ['...'] + list(range(d - 10, d))
        else:
            self._pages = list(range(1, self._pages_count + 1))

    def represent(self):
        return {
            "value": self._page,
            "values": self._pages,
            "max_value": self._pages_count,
            "limits": {
                "value": self._limit,
                "values": self._limits,
            }
        }

class LinearPager(Pager):
    def pages_factory(self):
        if self._pages_count <= 10:
            self._pages = self.range(1, self._pages_count)
        else:
            if self._page <= 5:
                self._pages = list(range(1, min(self._pages_count, 10))) + ['...']

            if 5 < self._page <= self._pages_count - 5:
                self._pages = ['...'] + self.range(max(self._page - 4, 1), min(self._page + 4, self._pages_count)) + ['...']

            if self._page > self._pages_count - 5:
                self._pages = ['...'] + self.range(max(self._pages_count - 8, 1), self._pages_count)


class TableView(CollectionModel):
    """ Класс для представления коллекции в виде структуры данных пригодной для использования в шаблонизаторе """
    template = ""
    title = None
    header = []
    properties = []
    boundaries = {}
    params = {}
    sort = []
    filters = []


    record_exists_exception = CommonException("Row exists already")
    record_not_found_exception = CommonException("Row not found")

    def __init__(self, *boundaries, **kwargs):
        super().__init__(*boundaries, **kwargs)
        self._orders = {}
        for prop in filter(None, self.sort):
            self._orders.update({'{prop}-asc'.format(prop=prop): (prop, 'ASC')})
            self._orders.update({'{prop}-desc'.format(prop=prop): (prop, 'DESC')})

        for bounds in boundaries:
            self.boundaries.update(bounds)

    def rows(self, sort, skip=0, limit=None):
        """ Возвращает строки таблицы
        :return:
        """
        params = self.params.copy()
        if sort:
            params.update({'order': self._orders.get(sort)})

        if limit and limit > 0:
            params.update({"skip": skip, "limit": limit})

        rows = []
        for item in self.get_items(self.boundaries, params=params):
            rows.append([item.primary.value, item.stringify(self.properties)])

        return rows

    def set_sub_boundaries(self, sub_boundaries: dict):
        """ Устанавливаеь дополнительные ограничения на таблицу (Что-то вроде фильтра или поиска по таблице)
        :param sub_boundaries: Дополнительные условия выборки записей
        """
        self.boundaries.update(sub_boundaries)

    def represent(self, request: Request=None,
                  show_checkboxes=True,
                  show_add_button=True,
                  show_edit_button=True,
                  show_delete_button=True
    ):
        """ Возвращает коллекцию в виде пригодном для шаблонизатора """

        sort = request.get('sort', None)\
            if request.get('sort', None) in self._orders\
            else None

        pager = LinearPager(self, request)

        return {
            "template": self.template,
            "title": self.title,
            "header": [{
                "title": self.header[key],
                "sort": {"asc": self.sort[key] + "-asc", "desc": self.sort[key] + "-desc"} if len(self.sort) >= key + 1 and self.sort[key] is not None else None
            }
                for key, p in enumerate(self.properties)

            ],
            "rows": self.rows(sort, pager.offset, pager.limit),
            "sort": sort,
            "pager": pager.represent(),
            "show_checkboxes": show_checkboxes,
            "show_add_button": show_add_button,
            "show_edit_button": show_edit_button,
            "show_delete_button": show_delete_button,
        }

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
        model = self.get_item({self.mapper.primary.name(): request.get("row_id")})
        if model is None:
            raise self.record_not_found_exception
        model.load_from_array(dict(request.items())).save()

    # noinspection PyMethodOverriding
    def delete(self, request: Request):
        """ Удаление нескольких записей """
        pkeys = request.get("row_id")
        if not isinstance(pkeys, list):
            pkeys = [pkeys]
        super().delete({self.mapper.primary.name(): ("in", pkeys)})

    # noinspection PyMethodOverriding
    def fetch_one(self, request: Request):
        model = self.get_item({self.mapper.primary.name(): request.get("row_id")})
        if not model:
            raise self.record_not_found_exception

        data = model.stringify(self.mapper.get_properties())
        for p in self.mapper.get_properties():
            attr = model.__getattribute__(p)
            if isinstance(attr, EmbeddedObject):
                data[p] = attr.get_value()
            if isinstance(attr, EntityModel):
                data[p] = attr.primary.get_value(deep=True)

        data["row_id"] = model.primary.get_value(deep=True)
        return data
