

from mapex import EntityModel, CollectionModel
from z9.apps.{default}.mappers.common import ExampleMapper

class Examples(CollectionModel):
    mapper = ExampleMapper


class Example(EntityModel):
    mapper = ExampleMapper