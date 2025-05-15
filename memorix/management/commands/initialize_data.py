from django.core.management.base import BaseCommand

from common.constants import GAME_CATEGORIES
from common.leaderboard import update_category_leaderboard
from memorix.models import Category


class Command(BaseCommand):
    help = 'Initialize data for Memorix'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='Only load categories without initializing leaderboards',
        )
        parser.add_argument(
            '--leaderboards-only',
            action='store_true',
            help='Only initialize leaderboards without loading categories',
        )

    def handle(self, *args, **options):
        categories_only = options.get('categories_only')
        leaderboards_only = options.get('leaderboards_only')
        run_categories = not leaderboards_only or categories_only
        run_leaderboards = not categories_only or leaderboards_only

        if run_categories:
            self.load_categories()
        if run_leaderboards:
            self.initialize_leaderboard()

    def load_categories(self):
        """Load predefined categories into the database"""
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

    def initialize_leaderboard(self):
        """Initialize leaderboards for all categories"""
        categories = Category.objects.all()
        updated_count = 0

        for category in categories:
            update_category_leaderboard(category)
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Initialized leaderboard for {updated_count} categories'
            )
        )
