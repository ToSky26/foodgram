import json
from typing import ClassVar
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    fixture_name: ClassVar[str]

    def handle(self, *args, **options):
        try:
            fixture_path = (
                Path(settings.BASE_DIR)
                / 'data'
                / self.fixture_name
            )

            with fixture_path.open(encoding='utf-8') as file:
                data = json.load(file)

            objects = [
                self.model(**row)
                for row in data
            ]

            created = len(
                self.model.objects.bulk_create(
                    objects,
                    ignore_conflicts=True,
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.fixture_name}: '
                    f'добавлено {created} записей.'
                )
            )

        except Exception as error:
            self.stderr.write(
                self.style.ERROR(str(error))
            )
