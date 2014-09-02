
from z9.core.models import Application
from envi import Controller

class DefaultController(Controller):
    default_action = "root"

    @staticmethod
    def root(**kwargs):
        """
        Title page
        :param kwargs:
        :return:
        """
        return "Hello, this is your new application called '{default}'!"

application = Application()
application.route("/", DefaultController)


