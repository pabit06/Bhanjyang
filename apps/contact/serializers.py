"""
Contact App DRF Serializers

Serializers for Contact API endpoints.

Author: Bhanjyang Tech Team
Created: 2026-01-06
"""

from rest_framework import serializers
from .models import ContactSubmission, PrivacyPolicy
from apps.about.models import Staff
from .utils import SpamDetectionService


class ContactSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for contact form submissions via API."""
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'subject',
            'message',
            'attachment',
            'submitted_at',
            'status'
        ]
        read_only_fields = ['id', 'submitted_at', 'status']
    
    def validate_message(self, value):
        """Check for spam in message."""
        if SpamDetectionService.is_spam(value):
            raise serializers.ValidationError(
                "Message detected as spam. Please remove spam content."
            )
        return value
    
    def validate(self, data):
        """Additional validation."""
        # Check attachment size if provided
        if 'attachment' in data and data['attachment']:
            max_size = 5 * 1024 * 1024  # 5MB
            if data['attachment'].size > max_size:
                raise serializers.ValidationError({
                    'attachment': 'File size must be less than 5MB.'
                })
        
        return data


class ContactSubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact submissions (no status visible)."""
    
    class Meta:
        model = ContactSubmission
        fields = [
            'name',
            'email',
            'phone',
            'subject',
            'message',
            'attachment'
        ]
    
    def validate_message(self, value):
        """Check for spam."""
        if SpamDetectionService.is_spam(value):
            raise serializers.ValidationError("Spam detected.")
        return value


class InformationOfficerSerializer(serializers.ModelSerializer):
    """
    Serializer for RTI Officer information.
    Uses apps.about.models.Staff
    """
    
    full_name = serializers.CharField(source='person.full_name', read_only=True)
    photo_url = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.CharField(source='person.phone', read_only=True)
    appointed_date = serializers.DateField(source='start_date', read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'id',
            'full_name',
            'position',
            'email',
            'phone',
            'photo_url',
            'appointed_date'
        ]
    
    def get_photo_url(self, obj):
        """Get absolute URL for photo."""
        request = self.context.get('request')
        if obj.person.photo and request:
            return request.build_absolute_uri(obj.person.photo.url)
        return None
    
    def get_email(self, obj):
        """Get RTI email or default."""
        return obj.get_rti_email()


class PrivacyPolicySerializer(serializers.ModelSerializer):
    """Serializer for privacy policy."""
    
    class Meta:
        model = PrivacyPolicy
        fields = [
            'id',
            'title',
            'content',
            'last_updated',
            'version',
            'is_active'
        ]
        read_only_fields = ['id', 'last_updated', 'is_active']


class ContactStatsSerializer(serializers.Serializer):
    """Serializer for contact statistics (admin)."""
    
    total_submissions = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    replied_count = serializers.IntegerField()
    spam_count = serializers.IntegerField()
    today_count = serializers.IntegerField()
    this_week_count = serializers.IntegerField()
    this_month_count = serializers.IntegerField()
