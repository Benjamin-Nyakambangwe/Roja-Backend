from django.core.management.base import BaseCommand
from daphne.cli import CommandLineInterface

class Command(BaseCommand):
    help = 'Runs the server with Daphne'

    def handle(self, *args, **options):
        cli = CommandLineInterface()
        cli.run(['core.asgi:application'] + list(args))