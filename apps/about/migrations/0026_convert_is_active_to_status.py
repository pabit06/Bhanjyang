# Generated manually

from django.db import migrations
from django.utils import timezone


def convert_is_active_to_status(apps, schema_editor):
    """Convert existing is_active=True records to status=PUBLISHED"""
    CooperativeInfo = apps.get_model('about', 'CooperativeInfo')
    CooperativeTimeline = apps.get_model('about', 'CooperativeTimeline')
    CooperativeStatistic = apps.get_model('about', 'CooperativeStatistic')
    CooperativeAffiliation = apps.get_model('about', 'CooperativeAffiliation')
    LeadershipMessage = apps.get_model('about', 'LeadershipMessage')
    
    now = timezone.now()
    
    # Convert CooperativeInfo
    CooperativeInfo.objects.filter(is_active=True).update(
        status='PB',  # PUBLISHED
        published_date=now
    )
    
    # Convert CooperativeTimeline
    CooperativeTimeline.objects.filter(is_active=True).update(
        status='PB',  # PUBLISHED
        published_date=now
    )
    
    # Convert CooperativeStatistic
    CooperativeStatistic.objects.filter(is_active=True).update(
        status='PB',  # PUBLISHED
        published_date=now
    )
    
    # Convert CooperativeAffiliation
    CooperativeAffiliation.objects.filter(is_active=True).update(
        status='PB',  # PUBLISHED
        published_date=now
    )
    
    # Convert LeadershipMessage
    LeadershipMessage.objects.filter(is_active=True).update(
        status='PB',  # PUBLISHED
        published_date=now
    )


def reverse_convert_status_to_is_active(apps, schema_editor):
    """Reverse migration: set is_active based on status"""
    CooperativeInfo = apps.get_model('about', 'CooperativeInfo')
    CooperativeTimeline = apps.get_model('about', 'CooperativeTimeline')
    CooperativeStatistic = apps.get_model('about', 'CooperativeStatistic')
    CooperativeAffiliation = apps.get_model('about', 'CooperativeAffiliation')
    LeadershipMessage = apps.get_model('about', 'LeadershipMessage')
    
    # Set is_active=True for PUBLISHED status
    CooperativeInfo.objects.filter(status='PB').update(is_active=True)
    CooperativeTimeline.objects.filter(status='PB').update(is_active=True)
    CooperativeStatistic.objects.filter(status='PB').update(is_active=True)
    CooperativeAffiliation.objects.filter(status='PB').update(is_active=True)
    LeadershipMessage.objects.filter(status='PB').update(is_active=True)
    
    # Set is_active=False for others
    CooperativeInfo.objects.exclude(status='PB').update(is_active=False)
    CooperativeTimeline.objects.exclude(status='PB').update(is_active=False)
    CooperativeStatistic.objects.exclude(status='PB').update(is_active=False)
    CooperativeAffiliation.objects.exclude(status='PB').update(is_active=False)
    LeadershipMessage.objects.exclude(status='PB').update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0025_cooperativeaffiliation_published_by_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_is_active_to_status, reverse_convert_status_to_is_active),
    ]
