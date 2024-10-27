# from django.core.management.base import BaseCommand
# from daphne.cli import CommandLineInterface

# class Command(BaseCommand):
#     help = 'Runs the server with Daphne'

#     def handle(self, *args, **options):
#         cli = CommandLineInterface()
#         cli.run(['core.asgi:application'] + list(args))





from django.core.management.base import BaseCommand
from daphne.cli import CommandLineInterface

class Command(BaseCommand):
    help = 'Runs the server with Daphne'

    def add_arguments(self, parser):
        parser.add_argument('bind', nargs='?', default='127.0.0.1:8000',
                          help='Optional host:port binding')

    def handle(self, *args, **options):
        cli = CommandLineInterface()
        bind = options.get('bind', '127.0.0.1:8000')
        host, port = bind.split(':') if ':' in bind else (bind, '8000')
        
        cli.run([
            'core.asgi:application',
            '-b', host,
            '-p', port
        ])