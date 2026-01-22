# news_events/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging
from .models import NewsArticle, Event, Category, Subscriber, Comment, Newsletter
from .security import ContentSecurityValidator, SpamProtectionManager, EmailSecurityManager

logger = logging.getLogger(__name__)

class NewsArticleForm(forms.ModelForm):
    """Enhanced form for news articles"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add asterisk to required field labels
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *" if field.label else f"{field_name} *"
    
    class Meta:
        model = NewsArticle
        fields = [
            'title', 'category', 'content', 'excerpt', 'image', 'image_alt',
            'status', 'priority', 'published_date', 'scheduled_date',
            'meta_title', 'meta_description', 'meta_keywords',
            'is_featured', 'allow_comments', 'require_login'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter article title'),
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': _('Write article content here...')
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Brief article summary (optional)'),
                'maxlength': '500'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SEO Title (optional)'),
                'maxlength': '200'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('SEO description (optional)'),
                'maxlength': '300'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SEO Keywords (comma separated)'),
                'maxlength': '500'
            }),
            'image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Alt text for image'),
                'maxlength': '200'
            }),
        }

    def clean_content(self):
        """Validate and sanitize content"""
        content = self.cleaned_data.get('content')
        if content:
            # Validate content security
            try:
                security_result = ContentSecurityValidator.validate_content_security(content, 'article')
                if not security_result['is_valid']:
                    raise ValidationError(_("Content has security issues."))
            except ValidationError:
                raise
            except Exception:
                raise ValidationError(_("Content validation failed."))
            
            # Sanitize content
            content = ContentSecurityValidator.sanitize_content(content)
        
        return content

    def clean_title(self):
        """Validate title"""
        title = self.cleaned_data.get('title')
        if title and len(title) > 200:
            raise ValidationError(_("Title must be 200 characters or less."))
        return title

    def clean_scheduled_date(self):
        """Validate scheduled date"""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        status = self.cleaned_data.get('status')
        
        if status == NewsArticle.Status.SCHEDULED and not scheduled_date:
            raise ValidationError(_("Scheduled date is required for scheduled articles."))
        
        if scheduled_date and scheduled_date <= timezone.now():
            raise ValidationError(_("Scheduled date must be in the future."))
        
        return scheduled_date

class EventForm(forms.ModelForm):
    """Enhanced form for events"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add asterisk to required field labels
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *" if field.label else f"{field_name} *"
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 'event_type',
            'location', 'address', 'event_date', 'end_date',
            'max_attendees', 'registration_required', 'registration_deadline',
            'registration_url', 'image', 'image_alt', 'status', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter event title'),
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('Write event description here...')
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Brief event description'),
                'maxlength': '300'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Event location'),
                'maxlength': '150'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Full event address')
            }),
            'registration_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/register'
            }),
            'image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Alt text for image'),
                'maxlength': '200'
            }),
        }

    def clean_description(self):
        """Validate and sanitize description"""
        description = self.cleaned_data.get('description')
        if description:
            # Validate content security
            try:
                security_result = ContentSecurityValidator.validate_content_security(description, 'event')
                if not security_result['is_valid']:
                    raise ValidationError(_("Description has security issues."))
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(_("Description validation failed."))
            
            # Sanitize content
            description = ContentSecurityValidator.sanitize_content(description)
        
        return description

    def clean_end_date(self):
        """Validate end date"""
        end_date = self.cleaned_data.get('end_date')
        event_date = self.cleaned_data.get('event_date')
        
        if end_date and event_date and end_date <= event_date:
            raise ValidationError(_("End date must be after event date."))
        
        return end_date

    def clean_registration_deadline(self):
        """Validate registration deadline"""
        registration_deadline = self.cleaned_data.get('registration_deadline')
        event_date = self.cleaned_data.get('event_date')
        registration_required = self.cleaned_data.get('registration_required')
        
        if registration_required and not registration_deadline:
            raise ValidationError(_("Registration deadline is required when registration is required."))
        
        if registration_deadline and event_date and registration_deadline >= event_date:
            raise ValidationError(_("Registration deadline must be before event date."))
        
        return registration_deadline

class CategoryForm(forms.ModelForm):
    """Form for categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Category name'),
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Category description')
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#28A745'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-newspaper',
                'maxlength': '50'
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }

class SubscriptionForm(forms.ModelForm):
    """Enhanced subscription form with security"""
    
    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'last_name', 'categories', 'frequency']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 text-gray-800 rounded-l-lg border-2 border-gray-300 focus:outline-none focus:border-deuraligreen transition-colors',
                'placeholder': _('Enter your email address...'),
                'aria-label': _('Email address'),
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First name (optional)'),
                'maxlength': '100'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Last name (optional)'),
                'maxlength': '100'
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_email(self):
        """Validate email security"""
        email = self.cleaned_data.get('email')
        if email:
            is_valid, reason = EmailSecurityManager.validate_email_security(email)
            if not is_valid:
                raise ValidationError(reason)
        return email

class CommentForm(forms.ModelForm):
    """Enhanced comment form with spam protection"""
    
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'content']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your Name'),
                'maxlength': '100',
                'required': True
            }),
            'author_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your email address'),
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Write your comment...'),
                'maxlength': '2000',
                'required': True
            }),
        }

    def clean_content(self):
        """Validate comment content for spam"""
        content = self.cleaned_data.get('content')
        if content:
            # Check for spam
            spam_check = SpamProtectionManager.check_spam_indicators(content)
            if spam_check['is_spam']:
                raise ValidationError(_("Comment looks like spam. Please review."))
            
            # Sanitize content
            content = ContentSecurityValidator.sanitize_content(content)
        
        return content

    def clean_author_email(self):
        """Validate author email"""
        email = self.cleaned_data.get('author_email')
        if email:
            is_valid, reason = EmailSecurityManager.validate_email_security(email)
            if not is_valid:
                raise ValidationError(reason)
        return email

class NewsletterForm(forms.ModelForm):
    """Form for newsletter campaigns"""
    
    class Meta:
        model = Newsletter
        fields = [
            'title', 'subject', 'content', 'categories', 'send_to_all',
            'scheduled_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Newsletter title'),
                'maxlength': '200'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email subject line'),
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': _('Newsletter content...')
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def clean_content(self):
        """Validate newsletter content"""
        content = self.cleaned_data.get('content')
        if content:
            # Validate content security
            try:
                security_result = ContentSecurityValidator.validate_content_security(content, 'newsletter')
                if not security_result['is_valid']:
                    raise ValidationError(_("सामग्रीमा सुरक्षा समस्या छ।"))
            except ValidationError:
                raise
            except Exception:
                raise ValidationError(_("Content validation failed."))
            
            # Sanitize content
            content = ContentSecurityValidator.sanitize_content(content)
        
        return content

    def clean_scheduled_date(self):
        """Validate scheduled date"""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        
        if scheduled_date and scheduled_date <= timezone.now():
            raise ValidationError(_("Scheduled date must be in the future."))
        
        return scheduled_date

class ContentSearchForm(forms.Form):
    """Advanced search form for content"""
    
    SEARCH_CHOICES = [
        ('all', _('All Content')),
        ('articles', _('Articles Only')),
        ('events', _('Events Only')),
    ]
    
    SORT_CHOICES = [
        ('relevance', _('Relevance')),
        ('date', _('Date')),
        ('views', _('Views')),
        ('title', _('Title')),
    ]
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search articles and events...'),
            'maxlength': '200'
        })
    )
    
    content_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    author = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label=_("All Authors"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', _('All Status')),
            ('published', _('Published Only')),
            ('draft', _('Draft Only')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    featured_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    has_image = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    min_read_time = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Minimum read time (min)'),
            'min': '0'
        })
    )
    max_read_time = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Maximum read time (min)'),
            'min': '0'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set authors queryset
        from django.contrib.auth.models import User
        self.fields['author'].queryset = User.objects.filter(
            news_events_articles__isnull=False
        ).distinct().order_by('username')

    def clean_date_to(self):
        """Validate date range"""
        date_from = self.cleaned_data.get('date_from')
        date_to = self.cleaned_data.get('date_to')
        
        if date_from and date_to and date_to < date_from:
            raise ValidationError(_("End date must be after start date."))
        
        return date_to

class BulkActionForm(forms.Form):
    """Form for bulk actions on content"""
    
    ACTION_CHOICES = [
        ('publish', _('Publish Selected')),
        ('draft', _('Move to Draft')),
        ('archive', _('Archive Selected')),
        ('delete', _('Delete Selected')),
        ('feature', _('Mark as Featured')),
        ('unfeature', _('Remove Featured')),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    content_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_content_ids(self):
        """Validate content IDs"""
        content_ids = self.cleaned_data.get('content_ids')
        if not content_ids:
            raise ValidationError(_("No content selected."))
        
        try:
            ids = [int(id.strip()) for id in content_ids.split(',') if id.strip()]
            if not ids:
                raise ValidationError(_("No valid content IDs provided."))
            return ids
        except ValueError:
            raise ValidationError(_("Invalid content ID provided."))
