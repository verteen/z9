

from mapex import EntityModel, CollectionModel
from z9.apps.{default}.databases.{default}.mappers import DefaultMapper

class Examples(CollectionModel):
    mapper = DefaultMapper


class Example(EntityModel):
    mapper = DefaultMapper