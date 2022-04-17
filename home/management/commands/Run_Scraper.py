from django.core.management.base import BaseCommand, CommandError
from FinvizScreeningScraper import main


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
        return

