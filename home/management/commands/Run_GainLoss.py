from django.core.management.base import BaseCommand, CommandError
from FindSuccessOverTime import main


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
        return