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
                created = len(
                    self.model.objects.bulk_create(
                        (self.model(**row) for row in json.load(file)),
                        ignore_conflicts=True,))

            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.fixture_name}: успешно импортировано ({created}).'
                )
            )

        except Exception as error:
            self.stderr.write(
                self.style.ERROR(f'{self.fixture_name}: {error}')
            )
