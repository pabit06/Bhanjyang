"""
REST API Serializers for News Events App.

Provides serialization for NewsArticle, Event, Category, Comment, Subscriber, and Newsletter models.
"""
from typing import Optional
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, get_language
from apps.core.templatetags.nepali_digits import to_nepali_digits
from .models import (
    NewsArticle, Event, Category, Comment, Subscriber, Newsletter, ContentAnalytics
)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    article_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon',
            'is_active', 'sort_order', 'article_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'article_count', 'created_at', 'updated_at']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for article/event author (User model)."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class NewsArticleSerializer(serializers.ModelSerializer):
    """Serializer for NewsArticle model with enhanced fields."""
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True,
        required=False
    )
    read_time = serializers.ReadOnlyField()
    optimized_image_url = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    view_count_display = serializers.SerializerMethodField()
    read_time_display = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'category', 'category_id', 'author',
            'content', 'excerpt', 'image', 'image_alt', 'optimized_image_url',
            'status', 'status_display', 'priority', 'priority_display',
            'is_featured', 'view_count', 'view_count_display', 'share_count',
            'comment_count', 'read_time', 'read_time_display', 'published_date', 'created_at',
            'updated_at', 'last_accessed', 'url'
        ]
        read_only_fields = [
            'id', 'slug', 'view_count', 'share_count', 'comment_count',
            'read_time', 'created_at', 'updated_at', 'last_accessed'
        ]
    
    def get_optimized_image_url(self, obj: NewsArticle) -> Optional[str]:
        """Get optimized image URL if available."""
        if obj.image_thumbnail:
            try:
                return obj.image_thumbnail.url
            except (AttributeError, ValueError, Exception):
                pass
        if obj.image:
            try:
                return obj.image.url
            except (AttributeError, ValueError, Exception):
                pass
        return None
    
    def validate_title(self, value: str) -> str:
        """Validate article title."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Title cannot be empty."))
        if len(value) > 200:
            raise serializers.ValidationError(_("Title cannot exceed 200 characters."))
        return value.strip()
    
    def validate_content(self, value: str) -> str:
        """Validate article content."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Content cannot be empty."))
        return value.strip()
    
    def get_url(self, obj: NewsArticle) -> str:
        """Get absolute URL for the article."""
        return obj.get_absolute_url()

    def get_view_count_display(self, obj: NewsArticle) -> str:
        """Get localized view count."""
        return to_nepali_digits(obj.view_count)

    def get_read_time_display(self, obj: NewsArticle) -> str:
        """Get localized read time."""
        return to_nepali_digits(obj.read_time)


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model with enhanced fields."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    optimized_image_url = serializers.SerializerMethodField()
    view_count_display = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'event_type', 'event_type_display', 'status', 'status_display',
            'location', 'address', 'event_date', 'end_date',
            'image', 'image_alt', 'optimized_image_url',
            'is_featured', 'is_recurring', 'view_count', 'view_count_display', 'registration_count',
            'created_at', 'updated_at', 'last_accessed', 'url'
        ]
        read_only_fields = [
            'id', 'slug', 'view_count', 'registration_count',
            'created_at', 'updated_at', 'last_accessed'
        ]
    
    def get_optimized_image_url(self, obj: Event) -> Optional[str]:
        """Get optimized image URL if available."""
        if not obj.image:
            return None
        try:
            # Try to get optimized image URL from property if it exists
            if hasattr(obj, 'optimized_image_url'):
                return obj.optimized_image_url
            return obj.image.url if obj.image else None
        except (AttributeError, ValueError, Exception):
            return None
    
    def validate_title(self, value: str) -> str:
        """Validate event title."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Title cannot be empty."))
        if len(value) > 200:
            raise serializers.ValidationError(_("Title cannot exceed 200 characters."))
        return value.strip()
    
    def validate_event_date(self, value):
        """Validate event date is not in the past (for new events)."""
        if value and value < timezone.now():
            # Allow past dates for existing events (update case)
            if not self.instance:  # New event
                raise serializers.ValidationError(_("Event date cannot be in the past."))
        return value
    
    def get_url(self, obj: Event) -> str:
        """Get absolute URL for the event."""
        return obj.get_absolute_url()

    def get_view_count_display(self, obj: Event) -> str:
        """Get localized view count."""
        return to_nepali_digits(obj.view_count)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    article_title = serializers.CharField(source='article.title', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'article_title', 'author_name', 'author_email',
            'content', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_author_name(self, value: str) -> str:
        """Validate author name."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Author name cannot be empty."))
        if len(value) > 100:
            raise serializers.ValidationError(_("Author name cannot exceed 100 characters."))
        return value.strip()
    
    def validate_author_email(self, value: str) -> str:
        """Validate author email."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Author email cannot be empty."))
        # Basic email validation
        if '@' not in value or '.' not in value.split('@')[1]:
            raise serializers.ValidationError(_("Please enter a valid email address."))
        return value.strip().lower()
    
    def validate_content(self, value: str) -> str:
        """Validate comment content."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Comment content cannot be empty."))
        if len(value) < 10:
            raise serializers.ValidationError(_("Comment must be at least 10 characters long."))
        if len(value) > 2000:
            raise serializers.ValidationError(_("Comment cannot exceed 2000 characters."))
        return value.strip()


class SubscriberSerializer(serializers.ModelSerializer):
    """Serializer for Subscriber model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscriber
        fields = [
            'id', 'email', 'first_name', 'last_name', 'status', 'status_display',
            'is_confirmed', 'subscribed_at',
            'last_activity', 'categories'
        ]
        read_only_fields = [
            'id', 'subscribed_at', 'last_activity'
        ]
    
    def validate_email(self, value: str) -> str:
        """Validate subscriber email."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Email cannot be empty."))
        value = value.strip().lower()
        # Basic email validation
        if '@' not in value or '.' not in value.split('@')[1]:
            raise serializers.ValidationError(_("Please enter a valid email address."))
        # Check for duplicate
        if self.instance is None:  # New subscriber
            if Subscriber.objects.filter(email=value).exists():
                raise serializers.ValidationError(_("This email is already subscribed."))
        return value


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'subject', 'content', 'status', 'status_display',
            'send_to_all', 'categories', 'category_names',
            'scheduled_date', 'sent_date', 'total_sent', 'total_opened',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sent_date', 'total_sent', 'total_opened',
            'created_at', 'updated_at'
        ]
    
    def get_category_names(self, obj: Newsletter) -> list:
        """Get list of category names."""
        return [cat.name for cat in obj.categories.all()]


class ContentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for ContentAnalytics model."""
    
    class Meta:
        model = ContentAnalytics
        fields = [
            'id', 'content_type', 'content_id', 'views',
            'shares', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'views', 'shares', 'comments',
            'created_at', 'updated_at'
        ]


class NewsArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article lists."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.SerializerMethodField()
    image_thumbnail = serializers.SerializerMethodField()
    view_count_display = serializers.SerializerMethodField()
    read_time_display = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category_name',
            'author_name', 'image_thumbnail', 'status', 'is_featured',
            'view_count', 'view_count_display', 'published_date', 'read_time', 'read_time_display', 'url'
        ]
        read_only_fields = ['id', 'slug', 'view_count', 'read_time']
    
    def get_image_thumbnail(self, obj: NewsArticle) -> Optional[str]:
        """Get thumbnail URL if available."""
        if not obj.image:
            return None
        try:
            if obj.image_thumbnail:
                return obj.image_thumbnail.url
        except (AttributeError, ValueError, Exception):
            pass
        return None
    
    def get_author_name(self, obj: NewsArticle) -> str:
        """Get author's full name or username."""
        if obj.author.first_name or obj.author.last_name:
            return f"{obj.author.first_name} {obj.author.last_name}".strip()
        return obj.author.username
    
    def get_url(self, obj: NewsArticle) -> str:
        """Get absolute URL for the article."""
        return obj.get_absolute_url()

    def get_view_count_display(self, obj: NewsArticle) -> str:
        """Get localized view count."""
        return to_nepali_digits(obj.view_count)

    def get_read_time_display(self, obj: NewsArticle) -> str:
        """Get localized read time."""
        return to_nepali_digits(obj.read_time)


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    # Without this, DRF maps `image_thumbnail` straight to the imagekit
    # ImageSpecField and serialises the cache-file object itself. The JSON
    # encoder then tries to read it, imagekit goes looking for a source image,
    # and every event without one raises MissingSource - a 500 on the whole
    # list endpoint. Mirror NewsArticleListSerializer and emit a URL string.
    image_thumbnail = serializers.SerializerMethodField()
    view_count_display = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'event_type',
            'event_type_display', 'location', 'event_date', 'end_date',
            'image_thumbnail', 'status', 'is_featured', 'view_count',
            'registration_count', 'view_count_display', 'url'
        ]
        read_only_fields = ['id', 'slug', 'view_count', 'registration_count']

    def get_image_thumbnail(self, obj: Event) -> Optional[str]:
        """Get thumbnail URL if available."""
        if not obj.image:
            return None
        try:
            if obj.image_thumbnail:
                return obj.image_thumbnail.url
        except (AttributeError, ValueError, Exception):
            pass
        return None

    def get_url(self, obj: Event) -> str:
        """Get absolute URL for the event."""
        return obj.get_absolute_url()

    def get_view_count_display(self, obj: Event) -> str:
        """Get localized view count."""
        return to_nepali_digits(obj.view_count)

