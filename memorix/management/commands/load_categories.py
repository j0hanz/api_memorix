from django.core.management.base import BaseCommand

from common.constants import GAME_CATEGORIES
from memorix.models import Category


class Command(BaseCommand):
    help = 'Load initial categories for Memorix'

    def handle(self, *args, **kwargs):
        categories = GAME_CATEGORIES
        created_count = 0
        for cat in categories:
            _, created = Category.objects.get_or_create(
                code=cat['code'],
                defaults={
                    'name': cat['name'],
                    'description': cat['description'],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {created_count} new categories'
            )
        )
