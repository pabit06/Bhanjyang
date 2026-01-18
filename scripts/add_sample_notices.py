#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to add sample notices to the database."""
import os
import sys
import django
from datetime import timedelta

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
from django.utils import timezone

# Sample notices data
sample_notices = [
    {
        'title': 'वार्षिक साधारण सभा (AGM)',
        'content': '''सभी सदस्यहरूलाई सूचना

हाम्रो सहकारी संस्थाको वार्षिक साधारण सभा (AGM) मिति, समय र स्थानको बारेमा सूचना दिइरहेका छौं।

**मिति:** [मिति थप्नुहोस्]
**समय:** [समय थप्नुहोस्]
**स्थान:** सहकारी कार्यालय

सभी सदस्यहरूलाई उपस्थित हुन अनुरोध गरिन्छ। सभामा संस्थाको वार्षिक प्रतिवेदन, वित्तीय विवरण, र अन्य महत्वपूर्ण विषयहरू छलफल गरिनेछ।

धन्यवाद।''',
        'notice_type': Notice.Type.AGM,
        'is_pinned': True,
        'is_active': True,
    },
    {
        'title': 'ब्याज दर परिवर्तन सूचना',
        'content': '''सभी सदस्यहरूलाई सूचना

सहकारी संस्थाको नीति अनुसार, ब्याज दरहरूमा परिवर्तन गरिएको छ।

**नयाँ ब्याज दरहरू:**
- बचत खाता: [दर]%
- सावधिक जम्मा: [दर]%
- ऋण ब्याज: [दर]%

यो परिवर्तन [मिति] देखि लागू हुनेछ। विस्तृत जानकारीको लागि कार्यालयमा सम्पर्क गर्नुहोस्।

धन्यवाद।''',
        'notice_type': Notice.Type.URGENT,
        'is_pinned': True,
        'is_active': True,
    },
    {
        'title': 'भ्रमण कार्यक्रम सूचना',
        'content': '''सभी सदस्यहरूलाई सूचना

सहकारी संस्थाको तर्फबाट भ्रमण कार्यक्रम आयोजना गरिएको छ।

**भ्रमण स्थान:** [स्थान]
**मिति:** [मिति]
**समय:** [समय]
**लागत:** [रकम]

सहभागी हुन इच्छुक सदस्यहरूले [मिति] अघि कार्यालयमा दर्ता गर्नुहोस्। सीमित स्थान उपलब्ध छ।

धन्यवाद।''',
        'notice_type': Notice.Type.GENERAL,
        'is_pinned': False,
        'is_active': True,
    },
    {
        'title': 'ऋण अनुगमन र स्मरण',
        'content': '''सभी ऋणी सदस्यहरूलाई सूचना

तपाईंको ऋणको नियमित भुक्तानीको बारेमा स्मरण दिइरहेका छौं।

कृपया आफ्नो ऋणको नियमित किस्ता समयमै तिर्नुहोस्। ऋण भुक्तानीमा ढिलाइ भएमा ब्याज बढ्न सक्छ।

**सम्पर्क:**
- कार्यालय: [फोन नम्बर]
- समय: [कार्यालय समय]

कुनै प्रश्न वा समस्या भएमा कार्यालयमा सम्पर्क गर्नुहोस्।

धन्यवाद।''',
        'notice_type': Notice.Type.URGENT,
        'is_pinned': False,
        'is_active': True,
    },
    {
        'title': 'प्रशिक्षण कार्यक्रम सूचना',
        'content': '''सभी सदस्यहरूलाई सूचना

सहकारी संस्थाको तर्फबाट प्रशिक्षण कार्यक्रम आयोजना गरिएको छ।

**विषय:** [प्रशिक्षण विषय]
**मिति:** [मिति]
**समय:** [समय]
**स्थान:** [स्थान]

यो प्रशिक्षण सबै सदस्यहरूको लागि निःशुल्क छ। सहभागी हुन इच्छुक सदस्यहरूले [मिति] अघि कार्यालयमा दर्ता गर्नुहोस्।

**सम्पर्क:**
- कार्यालय: [फोन नम्बर]

धन्यवाद।''',
        'notice_type': Notice.Type.GENERAL,
        'is_pinned': False,
        'is_active': True,
    },
]

print("Adding sample notices...")
print("-" * 50)

created_count = 0
updated_count = 0

for notice_data in sample_notices:
    # Set published date (some recent, some older)
    days_ago = sample_notices.index(notice_data)
    published_date = timezone.now() - timedelta(days=days_ago)
    
    notice, created = Notice.objects.get_or_create(
        title=notice_data['title'],
        defaults={
            'content': notice_data['content'],
            'notice_type': notice_data['notice_type'],
            'is_pinned': notice_data['is_pinned'],
            'is_active': notice_data['is_active'],
            'published_date': published_date,
        }
    )
    
    if created:
        created_count += 1
        status = "[CREATED]"
    else:
        # Update existing notice
        notice.content = notice_data['content']
        notice.notice_type = notice_data['notice_type']
        notice.is_pinned = notice_data['is_pinned']
        notice.is_active = notice_data['is_active']
        notice.published_date = published_date
        notice.save()
        updated_count += 1
        status = "[UPDATED]"
    
    print(f"{status}: {notice.title} ({notice.get_notice_type_display()})")

print("-" * 50)
print(f"\nSuccess! Created: {created_count}, Updated: {updated_count}")
print(f"\nYou can now see notices at:")
print("  - Frontend: /news-events/notices/")
print("  - Admin: /admin/news_events/notice/")
