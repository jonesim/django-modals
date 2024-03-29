from django.apps import apps
from django.core.management.base import BaseCommand
from modal_examples.import_data import import_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_data(apps.get_app_config('modal_examples').path)
