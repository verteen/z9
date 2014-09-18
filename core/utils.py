""" Вспомогательные утитилиты """

import re
import os
import hashlib
from itertools import filterfalse, chain
from importlib import import_module
from inspect import getmembers
from fcntl import flock, LOCK_EX, LOCK_NB

root_path = "%s/../" % os.path.dirname(os.path.abspath(__file__))


def md5(string):
    """ Возвращает md5 от строки
    :param string: Строка для кодирования
    :return: Результат хэширования
    """
    return hashlib.md5(str(string).encode()).hexdigest()


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


def get_cyrillic_font_name():
    """ Устанавливает кириллический фонт и возвращает его имя для использования """
    from reportlab.pdfbase import pdfmetrics
    fname = '%s/sf/common/fonts/arial' % root_path
    face_name = 'ArialMT'
    cyr_face = pdfmetrics.EmbeddedType1Face(fname+'.afm', fname+'.pfb')
    cyrenc = pdfmetrics.Encoding('CP1251')
    cp1251 = (
        'afii10051', 'afii10052', 'quotesinglbase', 'afii10100', 'quotedblbase',
        'ellipsis', 'dagger', 'daggerdbl', 'Euro', 'perthousand', 'afii10058',
        'guilsinglleft', 'afii10059', 'afii10061', 'afii10060', 'afii10145',
        'afii10099', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright',
        'bullet', 'endash', 'emdash', 'tilde', 'trademark', 'afii10106',
        'guilsinglright', 'afii10107', 'afii10109', 'afii10108', 'afii10193',
        'space', 'afii10062', 'afii10110', 'afii10057', 'currency', 'afii10050',
        'brokenbar', 'section', 'afii10023', 'copyright', 'afii10053',
        'guillemotleft', 'logicalnot', 'hyphen', 'registered', 'afii10056',
        'degree', 'plusminus', 'afii10055', 'afii10103', 'afii10098', 'mu1',
        'paragraph', 'periodcentered', 'afii10071', 'afii61352', 'afii10101',
        'guillemotright', 'afii10105', 'afii10054', 'afii10102', 'afii10104',
        'afii10017', 'afii10018', 'afii10019', 'afii10020', 'afii10021',
        'afii10022', 'afii10024', 'afii10025', 'afii10026', 'afii10027',
        'afii10028', 'afii10029', 'afii10030', 'afii10031', 'afii10032',
        'afii10033', 'afii10034', 'afii10035', 'afii10036', 'afii10037',
        'afii10038', 'afii10039', 'afii10040', 'afii10041', 'afii10042',
        'afii10043', 'afii10044', 'afii10045', 'afii10046', 'afii10047',
        'afii10048', 'afii10049', 'afii10065', 'afii10066', 'afii10067',
        'afii10068', 'afii10069', 'afii10070', 'afii10072', 'afii10073',
        'afii10074', 'afii10075', 'afii10076', 'afii10077', 'afii10078',
        'afii10079', 'afii10080', 'afii10081', 'afii10082', 'afii10083',
        'afii10084', 'afii10085', 'afii10086', 'afii10087', 'afii10088',
        'afii10089', 'afii10090', 'afii10091', 'afii10092', 'afii10093',
        'afii10094', 'afii10095', 'afii10096', 'afii10097'
    )
    for i in range(128, 256):
        cyrenc[i] = cp1251[i-128]
    pdfmetrics.registerEncoding(cyrenc)
    pdfmetrics.registerTypeFace(cyr_face)
    pdfmetrics.registerFont(pdfmetrics.Font(face_name+'1251', face_name, 'CP1251'))
    return face_name+'1251'


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

