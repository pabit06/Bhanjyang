"""
Management command to fetch exchange rates from NRB API.

This can be used manually or scheduled via cron for automatic fetching.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.services.services import ExchangeRateService


class Command(BaseCommand):
    help = 'Fetch latest exchange rates from Nepal Rastra Bank (NRB) API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to fetch rates for (YYYY-MM-DD format). Defaults to today.',
        )

    def handle(self, *args, **options):
        date_str = options.get('date')
        
        if date_str:
            from datetime import datetime
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid date format: {date_str}. Use YYYY-MM-DD format.')
                )
                return
        else:
            date = timezone.now().date()
        
        self.stdout.write(f'Fetching exchange rates from NRB for {date}...')
        
        try:
            count = ExchangeRateService.fetch_nrb_rates(date)
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully fetched {count} exchange rate(s) from NRB for {date}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'No exchange rates were fetched from NRB for {date}. '
                        'This might mean rates are not available for this date or the API returned no data.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching exchange rates: {str(e)}')
            )
            raise

