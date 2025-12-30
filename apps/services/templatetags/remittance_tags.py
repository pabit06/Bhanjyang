"""
Template tags for remittance services.
"""
from django import template
from django.templatetags.static import static

register = template.Library()

# Flag code mapping for static files
FLAG_MAP = {
    'USD': 'us', 'EUR': 'eu', 'GBP': 'gb', 'AUD': 'au', 'CAD': 'ca',
    'JPY': 'jp', 'INR': 'in', 'AED': 'ae', 'SAR': 'sa', 'QAR': 'qa',
    'SGD': 'sg', 'MYR': 'my', 'THB': 'th', 'CHF': 'ch', 'CNY': 'cn',
    'KWD': 'kw', 'BHD': 'bh', 'OMR': 'om', 'HKD': 'hk', 'NPR': 'np'
}


@register.simple_tag
def flag_image(currency_code, size='w40'):
    """
    Get the static path to a flag image for a currency.
    Prefers local static files, falls back to flagcdn.com.
    
    Usage: {% flag_image 'USD' %}
    Usage: {% flag_image 'USD' 'w40' %}
    
    Args:
        currency_code: ISO currency code (e.g., 'USD', 'EUR')
        size: Image size ('w40', 'w80', etc.) - defaults to 'w40'
    
    Returns:
        Static path to flag image, or fallback to flagcdn.com if not found locally
    """
    from django.conf import settings
    import os
    
    currency_code = currency_code.upper()
    flag_code = FLAG_MAP.get(currency_code)
    
    if flag_code:
        # Try local static file first
        static_path = f'images/flags/{flag_code}.png'
        # Check if file exists in static files
        static_file_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else '', static_path)
        
        # If local file exists, use it; otherwise fallback to CDN
        if os.path.exists(static_file_path):
            return static(static_path)
        else:
            # Fallback to flagcdn.com until flags are downloaded
            return f'https://flagcdn.com/{size}/{flag_code}.png'
    
    # Fallback to flagcdn.com if currency not in map
    return f'https://flagcdn.com/{size}/{currency_code.lower()}.png'


@register.simple_tag
def flag_image_local(currency_code, size='w40'):
    """
    Get the local static path to a flag image (assumes flags are downloaded).
    
    Usage: {% flag_image_local 'USD' %}
    
    This is the preferred method once flags are downloaded to static/images/flags/
    """
    currency_code = currency_code.upper()
    flag_code = FLAG_MAP.get(currency_code, currency_code.lower())
    return static(f'images/flags/{flag_code}.png')

