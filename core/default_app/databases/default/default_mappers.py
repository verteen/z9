
from mapex import MySqlClient, Contours, SqlMapper, Database


class DefaultMapper(SqlMapper):
    def bind(self):
        """ Настраиваем маппинг """
        from z9.apps.{default}.models.defaults import Defaults, Deafult

        self.set_new_item(Default)
        self.set_new_collection(Defaults)
        self.set_collection_name("Defaults")
        self.set_map([
            self.int("id", "ID"),
            self.str("name", "Name"),
            ])


database = Database(MySqlClient, {Contours.PRODUCTION: ("localhost", 3306, "root", "password", "{default}")})
database.register_mapper(DefaultMapper)