"""
Custom Django widgets including Nepali Datepicker widget
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NepaliDateInput(forms.TextInput):
    """
    Widget for Nepali date input using Nepali Datepicker library.
    
    Usage:
        class MyForm(forms.Form):
            date_field = forms.DateField(widget=NepaliDateInput(attrs={'class': 'form-control'}))
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'nepali-datepicker',
            'autocomplete': 'off',
            'readonly': 'readonly',  # Prevent manual typing, use picker only
        }
        if attrs:
            default_attrs.update(attrs)
        else:
            attrs = default_attrs
        
        # Ensure nepali-datepicker class is present
        if 'class' in attrs:
            if 'nepali-datepicker' not in attrs['class']:
                attrs['class'] += ' nepali-datepicker'
        else:
            attrs['class'] = 'nepali-datepicker'
        
        super().__init__(attrs)
    
    def format_value(self, value):
        """Format date value for display in Nepali datepicker - convert AD to BS"""
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            # Convert AD date to BS date for display in Nepali datepicker
            try:
                from nepali import datetime as nepali_datetime
                # Convert AD date to BS date using nepalidate.from_date()
                if hasattr(value, 'date'):
                    # It's a datetime object, extract date
                    ad_date = value.date()
                elif hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
                    # It's already a date object
                    ad_date = value
                else:
                    ad_date = value
                
                # Convert AD date to BS date
                bs_date = nepali_datetime.nepalidate.from_date(ad_date)
                # Return BS date in YYYY-MM-DD format
                return bs_date.strftime('%Y-%m-%d')
            except (ImportError, AttributeError, Exception) as e:
                logger.warning(f"Could not convert to BS date: {e}. Using AD date format.")
                # Fallback to AD date format
                return value.strftime('%Y-%m-%d')
        return str(value)
    
    class Media:
        css = {
            'all': ('vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.css',)
        }
        js = (
            'vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.js',
            'js/vendor/nepali-datepicker-init.js',
        )


class NepaliDateTimeInput(forms.TextInput):
    """
    Widget for Nepali datetime input using Nepali Datepicker library.
    The datepicker outputs English date in YYYY-MM-DD format which Django can parse.
    For DateTimeField, we need to ensure the value includes time component.
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'nepali-datepicker',
            'autocomplete': 'off',
            'readonly': 'readonly',
        }
        if attrs:
            default_attrs.update(attrs)
        else:
            attrs = default_attrs
        
        # Ensure nepali-datepicker class is present
        if 'class' in attrs:
            if 'nepali-datepicker' not in attrs['class']:
                attrs['class'] += ' nepali-datepicker'
        else:
            attrs['class'] = 'nepali-datepicker'
        
        super().__init__(attrs)
    
    def format_value(self, value):
        """Format datetime value for display in Nepali datepicker - convert AD to BS"""
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            # Convert AD datetime to BS date for display in Nepali datepicker
            try:
                from nepali import datetime as nepali_datetime
                # Extract date from datetime if needed
                if hasattr(value, 'date'):
                    # It's a datetime object, extract date
                    ad_date = value.date()
                elif hasattr(value, 'year') and hasattr(value, 'month') and hasattr(value, 'day'):
                    # It's already a date object
                    ad_date = value
                else:
                    # Try to parse as string or use as-is
                    ad_date = value
                
                # Convert AD date to BS date using nepalidate.from_date()
                # from_date expects a date object
                if hasattr(ad_date, 'year') and hasattr(ad_date, 'month') and hasattr(ad_date, 'day'):
                    # It's a date object, use from_date
                    bs_date = nepali_datetime.nepalidate.from_date(ad_date)
                elif hasattr(value, 'date'):
                    # It's a datetime, extract date first
                    bs_date = nepali_datetime.nepalidate.from_date(value.date())
                else:
                    # Try to use as-is (shouldn't happen, but fallback)
                    from datetime import datetime, date
                    if isinstance(ad_date, datetime):
                        bs_date = nepali_datetime.nepalidate.from_date(ad_date.date())
                    elif isinstance(ad_date, date):
                        bs_date = nepali_datetime.nepalidate.from_date(ad_date)
                    else:
                        raise ValueError(f"Unsupported date type: {type(ad_date)}")
                
                # Return BS date in YYYY-MM-DD format
                return bs_date.strftime('%Y-%m-%d')
            except (ImportError, AttributeError, Exception) as e:
                logger.error(f"Could not convert to BS date: {e}. Value type: {type(value)}. Using AD date format.")
                # Fallback to AD date format
                if hasattr(value, 'date'):
                    return value.date().strftime('%Y-%m-%d')
                return value.strftime('%Y-%m-%d')
        return str(value)
    
    def value_from_datadict(self, data, files, name):
        """Extract value from form data"""
        value = super().value_from_datadict(data, files, name)
        # Return the string value - let the form's clean method handle conversion
        return value
    
    class Media:
        css = {
            'all': ('vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.css',)
        }
        js = (
            'vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.js',
            'js/vendor/nepali-datepicker-init.js',
        )


class NepaliDateRangeInput(forms.TextInput):
    """
    Widget for Nepali date range input using Nepali Datepicker library.
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'nepali-datepicker-range',
            'autocomplete': 'off',
            'readonly': 'readonly',
        }
        if attrs:
            default_attrs.update(attrs)
        else:
            attrs = default_attrs
        
        if 'class' in attrs:
            if 'nepali-datepicker-range' not in attrs['class']:
                attrs['class'] += ' nepali-datepicker-range'
        else:
            attrs['class'] = 'nepali-datepicker-range'
        
        super().__init__(attrs)
    
    class Media:
        css = {
            'all': ('vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.css',)
        }
        js = (
            'vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.js',
            'js/vendor/nepali-datepicker-init.js',
        )

