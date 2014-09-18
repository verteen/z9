
from mapex import SqlMapper

class ExampleMapper(SqlMapper):
    def bind(self):
        """ Настраиваем маппинг """
        from z9.apps.{default}.models.common import Examples, Example

        self.set_new_item(Example)
        self.set_new_collection(Examples)
        self.set_collection_name("Defaults")
        self.set_map([
            self.int("id", "ID"),
            self.str("name", "Name"),
            ])