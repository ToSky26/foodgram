from recipes.models import Ingredient

from .base_import import BaseImportCommand


class Command(BaseImportCommand):
    model = Ingredient
    fixture_name = 'ingredients.json'
