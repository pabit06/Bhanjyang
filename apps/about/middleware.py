"""
Middleware to handle language preference for the site
"""
from django.utils import translation
from django.conf import settings


class ForceNepaliLanguageMiddleware:
    """
    Middleware that sets language based on user preference or defaults to Nepali.
    Checks session first, then cookie, then defaults to Nepali.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force Nepali for all URLs by default
        # Check for language preference in session (set by set_language view)
        # Django uses 'django_language' as the session key
        language = request.session.get('django_language')
        
        # If not in session, check cookie
        if not language:
            cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
            language = request.COOKIES.get(cookie_name)

            # If not in cookie either, force Nepali in session
            # This ensures LocaleMiddleware (which runs next) uses this preference
            # instead of the browser's Accept-Language header.
            if not language:
                request.session['django_language'] = 'ne'
                language = 'ne'
        
        # If still not set, use default (Nepali)
        if not language or language not in dict(settings.LANGUAGES):
            language = settings.LANGUAGE_CODE
        
        # Activate the language
        translation.activate(language)
        request.LANGUAGE_CODE = language
        
        response = self.get_response(request)
        
        # Set language cookie in response
        cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
        cookie_age = getattr(settings, 'LANGUAGE_COOKIE_AGE', 365 * 24 * 60 * 60)  # 1 year default
        cookie_path = getattr(settings, 'LANGUAGE_COOKIE_PATH', '/')
        
        response.set_cookie(
            cookie_name,
            language,
            max_age=cookie_age,
            path=cookie_path,
        )
        
        return response

