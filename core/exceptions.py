import re


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


class InvalidPhoneNumber(CommonException):
    """ Исключение, возникающее, если для форматирования передан некорректный телефонный номер """
    def __init__(self, number):
        self.message = "Некорректный номер телефона: %s" % number
        super().__init__()
