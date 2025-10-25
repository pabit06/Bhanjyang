from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.http import HttpResponse
import json

class Command(BaseCommand):
    help = 'Send sticky notice to frontend'

    def add_arguments(self, parser):
        parser.add_argument('--message', type=str, required=True, help='Notice message')
        parser.add_argument('--title', type=str, default='Notice', help='Notice title')
        parser.add_argument('--type', type=str, default='info', choices=['info', 'success', 'warning', 'error'], help='Notice type')
        parser.add_argument('--duration', type=int, default=5000, help='Duration in milliseconds')

    def handle(self, *args, **options):
        notice_data = {
            'message': options['message'],
            'title': options['title'],
            'type': options['type'],
            'duration': options['duration']
        }
        
        self.stdout.write(
            self.style.SUCCESS(f'Sticky notice created: {notice_data["type"].upper()} - {notice_data["title"]}')
        )
        self.stdout.write(f'Message: {notice_data["message"]}')
        self.stdout.write(f'Duration: {notice_data["duration"]}ms')
        
        # You can save this to database or send via WebSocket if needed
        return notice_data
