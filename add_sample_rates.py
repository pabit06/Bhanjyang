#!/usr/bin/env python
"""Quick script to add sample exchange rates for testing."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.services.models import ExchangeRate
from django.utils import timezone
from decimal import Decimal

# Sample exchange rates (approximate rates - update with real values)
sample_rates = [
    {'currency_code': 'USD', 'buy_rate': Decimal('133.50'), 'sell_rate': Decimal('134.00')},
    {'currency_code': 'EUR', 'buy_rate': Decimal('145.00'), 'sell_rate': Decimal('145.50')},
    {'currency_code': 'GBP', 'buy_rate': Decimal('170.00'), 'sell_rate': Decimal('170.50')},
    {'currency_code': 'AED', 'buy_rate': Decimal('36.30'), 'sell_rate': Decimal('36.50')},
    {'currency_code': 'SAR', 'buy_rate': Decimal('35.60'), 'sell_rate': Decimal('35.80')},
    {'currency_code': 'QAR', 'buy_rate': Decimal('36.70'), 'sell_rate': Decimal('36.90')},
    {'currency_code': 'KWD', 'buy_rate': Decimal('435.00'), 'sell_rate': Decimal('437.00')},
]

today = timezone.now().date()

print("Adding sample exchange rates...")
for rate_data in sample_rates:
    rate, created = ExchangeRate.objects.get_or_create(
        currency_code=rate_data['currency_code'],
        rate_date=today,
        defaults={
            'buy_rate': rate_data['buy_rate'],
            'sell_rate': rate_data['sell_rate'],
            'source': 'Manual',
            'is_active': True,
        }
    )
    status = "Created" if created else "Already exists"
    print(f"  {rate_data['currency_code']}: {status} - Buy: {rate.buy_rate}, Sell: {rate.sell_rate}")

print(f"\nSuccess! Added {len(sample_rates)} exchange rates for {today}")
print("\nYou can now see exchange rates at:")
print("  - Frontend: /services/remittance/")
print("  - Admin: /admin/services/exchangerate/")
print("  - API: /api/v1/exchange-rates/")

