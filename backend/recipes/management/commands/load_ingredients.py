from csv import DictReader

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open(
            'data/ingredients.csv',
            encoding='utf-8'
        ) as file:
            ingredients = [
                Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                for row in DictReader(file)
            ]

            Ingredient.objects.bulk_create(
                ingredients,
                ignore_conflicts=True
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Ингредиенты успешно загружены'
            )
        )
