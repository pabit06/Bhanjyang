"""
Management command to recalculate mid_rate for all ExchangeRate records.

This fixes any incorrect mid_rate values by recalculating them from buy_rate and sell_rate.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.services.models import ExchangeRate
from decimal import Decimal


class Command(BaseCommand):
    help = 'Recalculate mid_rate for all ExchangeRate records from buy_rate and sell_rate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--currency',
            type=str,
            help='Only recalculate rates for a specific currency code (e.g., USD)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        currency_filter = options.get('currency')
        
        # Build queryset
        queryset = ExchangeRate.objects.all()
        if currency_filter:
            queryset = queryset.filter(currency_code=currency_filter.upper())
        
        total_count = queryset.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('No exchange rate records found to update.')
            )
            return
        
        self.stdout.write(f'Found {total_count} exchange rate record(s) to process...')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        updated_count = 0
        corrected_count = 0
        
        with transaction.atomic():
            for rate in queryset:
                # Calculate correct mid_rate
                correct_mid_rate = (rate.buy_rate + rate.sell_rate) / Decimal('2')
                
                # Check if mid_rate needs correction
                if rate.mid_rate != correct_mid_rate:
                    old_mid_rate = rate.mid_rate
                    rate.mid_rate = correct_mid_rate
                    
                    if not dry_run:
                        # Call save() which will recalculate mid_rate using the model's logic
                        rate.save()
                    
                    corrected_count += 1
                    self.stdout.write(
                        f'  {rate.currency_code} ({rate.rate_date}): '
                        f'mid_rate {old_mid_rate} -> {correct_mid_rate}'
                    )
                else:
                    updated_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDRY RUN: Would correct {corrected_count} record(s), '
                    f'{updated_count} already correct'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully recalculated {corrected_count} mid_rate value(s). '
                    f'{updated_count} record(s) were already correct.'
                )
            )

