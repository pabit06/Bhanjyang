from django.core.management.commands.runserver import Command as RunserverCommand
from django.conf import settings

class Command(RunserverCommand):
    help = 'Run development server on default port from settings'
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--port',
            default=getattr(settings, 'DEFAULT_PORT', '5555'),
            help='Port to run the server on',
        )
    
    def handle(self, *args, **options):
        port = options['port']
        # Allow external access by using 0.0.0.0 instead of 127.0.0.1
        options['addrport'] = f"0.0.0.0:{port}"
        super().handle(*args, **options)
