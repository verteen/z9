
from z9.core.models import Application, Database, Contours, DbClients
from z9.apps.{default}.controllers.common import DefaultController


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