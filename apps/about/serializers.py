from rest_framework import serializers
from .models import (
    CooperativeInfo, CooperativeTimeline,
    CooperativeStatistic, CooperativeAffiliation, LeadershipMessage,
    Person, Committee, Membership, Staff
)


class CooperativeInfoSerializer(serializers.ModelSerializer):
    """Serializer for CooperativeInfo model"""
    
    class Meta:
        model = CooperativeInfo
        fields = [
            'id', 'cooperative_name', 'cooperative_name_nepali', 'slug',
            'description', 'description_nepali', 'mission', 'vision', 'values',
            'established_date', 'registration_number', 'license_number',
            'address', 'phone', 'email', 'website',
            'featured_image', 'logo', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class CooperativeTimelineSerializer(serializers.ModelSerializer):
    """Serializer for CooperativeTimeline model"""
    
    class Meta:
        model = CooperativeTimeline
        fields = [
            'id', 'title', 'description', 'event_date', 'event_type',
            'image', 'is_active', 'is_featured', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CooperativeStatisticSerializer(serializers.ModelSerializer):
    """Serializer for CooperativeStatistic model"""
    
    class Meta:
        model = CooperativeStatistic
        fields = [
            'id', 'title', 'value', 'unit', 'description',
            'is_active', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CooperativeAffiliationSerializer(serializers.ModelSerializer):
    """Serializer for CooperativeAffiliation model"""
    
    class Meta:
        model = CooperativeAffiliation
        fields = [
            'id', 'name', 'description', 'website', 'logo',
            'affiliation_type', 'is_active', 'is_featured', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeadershipMessageSerializer(serializers.ModelSerializer):
    """Serializer for LeadershipMessage model"""
    
    class Meta:
        model = LeadershipMessage
        fields = [
            'id', 'title', 'content', 'author_name', 'author_position',
            'author_photo', 'is_active', 'is_featured', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PersonSerializer(serializers.ModelSerializer):
    """Serializer for Person model"""
    
    class Meta:
        model = Person
        fields = [
            'id', 'full_name', 'bio', 'photo', 'email', 'phone',
            'position_general', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommitteeSerializer(serializers.ModelSerializer):
    """Serializer for Committee model"""
    
    class Meta:
        model = Committee
        fields = [
            'id', 'name', 'description', 'is_active', 'order'
        ]
        read_only_fields = ['id']


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model"""
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    committee_name = serializers.CharField(source='committee.name', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'person', 'person_name', 'committee', 'committee_name',
            'position', 'start_date', 'end_date', 'is_active'
        ]
        read_only_fields = ['id']


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff model"""
    person_name = serializers.CharField(source='person.full_name', read_only=True)
    person_photo = serializers.ImageField(source='person.photo', read_only=True)
    person_email = serializers.EmailField(source='person.email', read_only=True)
    person_phone = serializers.CharField(source='person.phone', read_only=True)
    rti_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = [
            'id', 'person', 'person_name', 'person_photo', 'person_email', 'person_phone',
            'position', 'department', 'start_date', 'is_active',
            'is_information_officer', 'information_officer_email', 'rti_email'
        ]
        read_only_fields = ['id', 'rti_email']
    
    def get_rti_email(self, obj):
        """Get the RTI email address"""
        return obj.get_rti_email() if obj.is_information_officer else None


# Nested serializers for detailed views
class DetailedCooperativeInfoSerializer(CooperativeInfoSerializer):
    """
    Detailed serializer for CooperativeInfo.
    
    Note: CooperativeInfo doesn't have direct ForeignKey relationships to other models.
    Use this serializer for the base cooperative info. Related data (statistics, timeline, etc.)
    should be fetched separately via their respective endpoints or service layer.
    """
    
    class Meta(CooperativeInfoSerializer.Meta):
        # Same fields as base serializer - related data fetched separately
        pass


class DetailedPersonSerializer(PersonSerializer):
    """Detailed serializer for Person with memberships and staff profile"""
    memberships = MembershipSerializer(many=True, read_only=True)
    staff_profile = StaffSerializer(read_only=True)
    
    class Meta(PersonSerializer.Meta):
        fields = PersonSerializer.Meta.fields + ['memberships', 'staff_profile']


class DetailedCommitteeSerializer(CommitteeSerializer):
    """Detailed serializer for Committee with members"""
    memberships = MembershipSerializer(many=True, read_only=True)
    
    class Meta(CommitteeSerializer.Meta):
        fields = CommitteeSerializer.Meta.fields + ['memberships']


# Summary serializers for list views
class SummaryCooperativeInfoSerializer(serializers.ModelSerializer):
    """Summary serializer for CooperativeInfo in list views"""
    
    class Meta:
        model = CooperativeInfo
        fields = ['id', 'cooperative_name', 'description', 'logo']


class SummaryPersonSerializer(serializers.ModelSerializer):
    """Summary serializer for Person in list views"""
    
    class Meta:
        model = Person
        fields = ['id', 'full_name', 'photo', 'position_general']


class SummaryTimelineSerializer(serializers.ModelSerializer):
    """Summary serializer for CooperativeTimeline in list views"""
    
    class Meta:
        model = CooperativeTimeline
        fields = ['id', 'title', 'event_date', 'event_type', 'image', 'is_featured']


# Custom field serializers
class ImageFieldSerializer(serializers.Field):
    """Custom serializer for image fields with full URL"""
    
    def to_representation(self, value):
        if value:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(value.url)
            return value.url
        return None


class DateFieldSerializer(serializers.Field):
    """Custom serializer for date fields with formatting"""
    
    def to_representation(self, value):
        if value:
            return value.strftime('%Y-%m-%d')
        return None


class DateTimeFieldSerializer(serializers.Field):
    """Custom serializer for datetime fields with formatting"""
    
    def to_representation(self, value):
        if value:
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return None
