#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Enable show_as_popup for AGM and Interest Change notices."""
import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.news_events.models import Notice

print("Enabling show_as_popup for notices...")
print("-" * 50)

# Enable for AGM notice
agm_notice = Notice.objects.filter(notice_type=Notice.Type.AGM, is_active=True).first()
if agm_notice:
    agm_notice.show_as_popup = True
    agm_notice.save()
    print(f"[UPDATED] {agm_notice.title} - show_as_popup enabled")
else:
    print("[NOT FOUND] AGM notice not found")

# Enable for Interest Change notice (URGENT type)
interest_notice = Notice.objects.filter(notice_type=Notice.Type.URGENT, is_active=True).first()
if interest_notice:
    interest_notice.show_as_popup = True
    interest_notice.save()
    print(f"[UPDATED] {interest_notice.title} - show_as_popup enabled")
else:
    print("[NOT FOUND] Interest change notice not found")

print("-" * 50)
print("\nDone! These notices will now appear as popups on the home page.")
print("\nNote: PopupNotice has higher priority. If a PopupNotice is active,")
print("it will show first. Regular notices will show only if no PopupNotice is active.")
