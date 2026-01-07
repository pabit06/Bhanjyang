"""
REST API Serializers for News Events App.

Provides serialization for NewsArticle, Event, Category, Comment, Subscriber, and Newsletter models.
"""
from typing import Optional
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
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
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'category', 'category_id', 'author',
            'content', 'excerpt', 'image', 'image_alt', 'optimized_image_url',
            'status', 'status_display', 'priority', 'priority_display',
            'is_featured', 'view_count', 'share_count',
            'comment_count', 'read_time', 'published_date', 'created_at',
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
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value.strip()
    
    def validate_content(self, value: str) -> str:
        """Validate article content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()
    
    def get_url(self, obj: NewsArticle) -> str:
        """Get absolute URL for the article."""
        return obj.get_absolute_url()


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model with enhanced fields."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    optimized_image_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'event_type', 'event_type_display', 'status', 'status_display',
            'location', 'address', 'event_date', 'end_date',
            'image', 'image_alt', 'optimized_image_url',
            'is_featured', 'is_recurring', 'view_count', 'registration_count',
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
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value.strip()
    
    def validate_event_date(self, value):
        """Validate event date is not in the past (for new events)."""
        if value and value < timezone.now():
            # Allow past dates for existing events (update case)
            if not self.instance:  # New event
                raise serializers.ValidationError("Event date cannot be in the past.")
        return value
    
    def get_url(self, obj: Event) -> str:
        """Get absolute URL for the event."""
        return obj.get_absolute_url()


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
            raise serializers.ValidationError("Author name cannot be empty.")
        if len(value) > 100:
            raise serializers.ValidationError("Author name cannot exceed 100 characters.")
        return value.strip()
    
    def validate_author_email(self, value: str) -> str:
        """Validate author email."""
        if not value or not value.strip():
            raise serializers.ValidationError("Author email cannot be empty.")
        # Basic email validation
        if '@' not in value or '.' not in value.split('@')[1]:
            raise serializers.ValidationError("Please enter a valid email address.")
        return value.strip().lower()
    
    def validate_content(self, value: str) -> str:
        """Validate comment content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty.")
        if len(value) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long.")
        if len(value) > 2000:
            raise serializers.ValidationError("Comment cannot exceed 2000 characters.")
        return value.strip()


class SubscriberSerializer(serializers.ModelSerializer):
    """Serializer for Subscriber model."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscriber
        fields = [
            'id', 'email', 'first_name', 'last_name', 'status', 'status_display',
            'is_confirmed', 'subscribed_at', 'unsubscribed_at',
            'last_activity', 'categories'
        ]
        read_only_fields = [
            'id', 'subscribed_at', 'unsubscribed_at', 'last_activity'
        ]
    
    def validate_email(self, value: str) -> str:
        """Validate subscriber email."""
        if not value or not value.strip():
            raise serializers.ValidationError("Email cannot be empty.")
        value = value.strip().lower()
        # Basic email validation
        if '@' not in value or '.' not in value.split('@')[1]:
            raise serializers.ValidationError("Please enter a valid email address.")
        # Check for duplicate
        if self.instance is None:  # New subscriber
            if Subscriber.objects.filter(email=value).exists():
                raise serializers.ValidationError("This email is already subscribed.")
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
            'id', 'content_type', 'object_id', 'view_count',
            'share_count', 'comment_count', 'last_accessed',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'view_count', 'share_count', 'comment_count',
            'last_accessed', 'created_at', 'updated_at'
        ]


class NewsArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article lists."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.SerializerMethodField()
    image_thumbnail = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category_name',
            'author_name', 'image_thumbnail', 'status', 'is_featured',
            'view_count', 'published_date', 'read_time', 'url'
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


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event lists."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'event_type',
            'event_type_display', 'location', 'event_date', 'end_date',
            'image_thumbnail', 'status', 'is_featured', 'view_count',
            'registration_count', 'url'
        ]
        read_only_fields = ['id', 'slug', 'view_count', 'registration_count']
    
    def get_url(self, obj: Event) -> str:
        """Get absolute URL for the event."""
        return obj.get_absolute_url()

