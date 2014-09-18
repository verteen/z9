
from z9.core.models import Application, Database, Contours, DbClients
from envi import Controller, template

class DefaultController(Controller):
    default_action = "root"

    @staticmethod
    @template("views.bootstrap")
    def root(**kwargs):
        """
        Title page
        :param kwargs:
        :return:
        """
        return "Hello, this is your new application called '{default}'! " \
               "If you see this text it means that your z9 setup is not correct. " \
               "You supposed to see a page made with bootstrap styles."


application = Application()
application.start_production()
application.route("/", DefaultController)
application.database(
    Database(
        DbClients.MYSQL,
        ["z9.apps.{default}.mappers.common"],
        {
            Contours.PRODUCTION: ("localhost", 3306, "root", "", "dbname"),
            Contours.BETA: ("localhost", 3306, "root", "", "dbname"),
            Contours.UNITTESTS: ("localhost", 3306, "root", "", "dbname")
        }
    )
)