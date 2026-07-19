import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV file'

    def handle(self, *args, **options):
        self.import_ingredients()
        self.stdout.write(self.style.SUCCESS('Импорт завершён.'))

    def import_ingredients(self):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        with open(file_path, encoding='utf-8') as f:
            ingredients = [
                Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                for row in csv.DictReader(
                    f, fieldnames=['name', 'measurement_unit']
                )
            ]

            Ingredient.objects.bulk_create(
                ingredients, ignore_conflicts=True
            )
