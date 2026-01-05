"""
Management command to manually send newsletters.

This command allows administrators to send newsletters manually or test
newsletter sending functionality.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.news_events.models import Newsletter, Subscriber
from apps.news_events.tasks import send_newsletter_email


class Command(BaseCommand):
    help = 'Manually send newsletter to subscribers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--newsletter-id',
            type=int,
            help='ID of newsletter to send'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Send test email to a single subscriber'
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Email address for test send (required with --test)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        newsletter_id = options.get('newsletter_id')
        test_mode = options['test']
        test_email = options.get('test_email')
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No emails will be sent'))
        
        if test_mode:
            if not test_email:
                self.stderr.write(self.style.ERROR(
                    '--test-email is required when using --test'
                ))
                return
            
            if not newsletter_id:
                self.stderr.write(self.style.ERROR(
                    '--newsletter-id is required when using --test'
                ))
                return
            
            try:
                newsletter = Newsletter.objects.get(pk=newsletter_id)
            except Newsletter.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f'Newsletter with ID {newsletter_id} not found'
                ))
                return
            
            # Create or get test subscriber
            subscriber, created = Subscriber.objects.get_or_create(
                email=test_email,
                defaults={
                    'name': 'Test Subscriber',
                    'status': Subscriber.Status.ACTIVE,
                    'is_confirmed': True,
                }
            )
            
            if not subscriber.is_confirmed:
                subscriber.is_confirmed = True
                subscriber.status = Subscriber.Status.ACTIVE
                subscriber.save()
            
            if dry_run:
                self.stdout.write(
                    f'Would send newsletter "{newsletter.subject}" to {test_email}'
                )
            else:
                # Send test email
                try:
                    send_newsletter_email(newsletter.id, subscriber.id)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Test email sent to {test_email}'
                        )
                    )
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f'Error sending test email: {str(e)}')
                    )
        
        else:
            if not newsletter_id:
                self.stderr.write(self.style.ERROR(
                    '--newsletter-id is required (or use --test for test send)'
                ))
                return
            
            try:
                newsletter = Newsletter.objects.get(pk=newsletter_id)
            except Newsletter.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f'Newsletter with ID {newsletter_id} not found'
                ))
                return
            
            # Get active confirmed subscribers
            subscribers = Subscriber.objects.filter(
                status=Subscriber.Status.ACTIVE,
                is_confirmed=True
            )
            
            subscriber_count = subscribers.count()
            
            if subscriber_count == 0:
                self.stdout.write(self.style.WARNING(
                    'No active confirmed subscribers found'
                ))
                return
            
            self.stdout.write(
                f'\nSending newsletter "{newsletter.subject}" to {subscriber_count} subscribers'
            )
            
            if dry_run:
                self.stdout.write(f'Would send to {subscriber_count} subscribers')
            else:
                sent_count = 0
                failed_count = 0
                
                for subscriber in subscribers:
                    try:
                        send_newsletter_email(newsletter.id, subscriber.id)
                        sent_count += 1
                    except Exception as e:
                        failed_count += 1
                        self.stderr.write(
                            self.style.WARNING(
                                f'Failed to send to {subscriber.email}: {str(e)}'
                            )
                        )
                
                # Update newsletter
                newsletter.status = Newsletter.Status.SENT
                newsletter.sent_date = timezone.now()
                newsletter.total_sent = sent_count
                newsletter.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nNewsletter sent: {sent_count} successful, {failed_count} failed'
                    )
                )

