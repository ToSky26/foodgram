import json

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open(
            'data/tags.json',
            encoding='utf-8'
        ) as file:
            tags = json.load(file)

        for tag in tags:
            Tag.objects.get_or_create(
                name=tag['name'],
                slug=tag['slug']
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Теги успешно загружены'
            )
        )
