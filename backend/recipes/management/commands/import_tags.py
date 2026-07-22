from recipes.models import Tag

from .base_import import BaseImportCommand


class Command(BaseImportCommand):
    model = Tag
    fixture_name = 'tags.json'
