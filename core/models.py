import re
from envi import Application as EnviApplication, ControllerMethodResponseWithTemplate
from suit.Suit import Suit, TemplateNotFound


class Application(EnviApplication):
    """ Стандартное приложение z9 """

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