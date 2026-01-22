#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to seed hero section content for home page."""
import os
import sys
import django

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.home.models import HomePageContent

# Hero slides data
hero_slides = [
    {
        'title': 'Empowering Your Financial Journey in Rupa',
        'subtitle': 'Welcome to Bhanjyang Cooperative',
        'description': 'Bhanjyang Cooperative is dedicated to fostering economic growth and community development in Rupa Rural Municipality through reliable and accessible financial services.',
        'order': 0,
        'primary_button_text': 'Explore Services',
        'primary_button_url': '/services/',
        'secondary_button_text': 'Contact Us',
        'secondary_button_url': '/contact/',
    },
    {
        'title': 'Secure Your Future with Smart Savings',
        'subtitle': 'Savings & Investments',
        'description': 'Our flexible savings plans offer competitive interest rates, helping you achieve your financial goals faster and with peace of mind.',
        'order': 1,
        'primary_button_text': 'View Savings Plans',
        'primary_button_url': '/services/savings/',
        'secondary_button_text': 'Open Account',
        'secondary_button_url': '/contact/',
    },
    {
        'title': 'Loans Tailored to Your Ambition',
        'subtitle': 'Loan Services',
        'description': 'Whether for personal needs, business expansion, or agricultural projects, our flexible loan products are designed to fuel your success.',
        'order': 2,
        'primary_button_text': 'Apply for a Loan',
        'primary_button_url': '/services/loans/',
        'secondary_button_text': 'Loan Calculator',
        'secondary_button_url': '/services/loan-calculator/',
    },
    {
        'title': 'Power of Cooperation - Remittance Services',
        'subtitle': 'Remittance Services',
        'description': 'Member empowerment and economic prosperity. Send money home safely and affordably with our trusted remittance partners including eSewa, Khalti, IME, and more.',
        'order': 3,
        'primary_button_text': 'Remittance Services',
        'primary_button_url': '/services/remittance/',
        'secondary_button_text': 'Contact Us',
        'secondary_button_url': '/contact/',
    },
]

print("Creating hero section content...")
print("=" * 60)

for slide_data in hero_slides:
    # Check if content with same title exists
    existing = HomePageContent.objects.filter(title=slide_data['title']).first()
    
    if existing:
        print(f"⚠️  Slide '{slide_data['title']}' already exists. Skipping...")
        continue
    
    # Create new HomePageContent
    content = HomePageContent.objects.create(
        title=slide_data['title'],
        subtitle=slide_data['subtitle'],
        description=slide_data['description'],
        order=slide_data['order'],
        is_active=True,
        primary_button_text=slide_data['primary_button_text'],
        primary_button_url=slide_data['primary_button_url'],
        secondary_button_text=slide_data['secondary_button_text'],
        secondary_button_url=slide_data['secondary_button_url'],
    )
    
    print(f"✅ Created: {content.title} (Order: {content.order})")

print("=" * 60)
print(f"✅ Successfully created {HomePageContent.objects.filter(is_active=True).count()} active hero slides!")
print("\nNote: You can add hero images through the admin panel at:")
print("   /admin/home/homepagecontent/")
