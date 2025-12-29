"""
Middleware to force Nepali language for About app
"""
from django.utils import translation


class ForceNepaliLanguageMiddleware:
    """
    Middleware that forces Nepali language for all requests.
    This overrides browser's Accept-Language header.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force Nepali language
        translation.activate('ne')
        request.LANGUAGE_CODE = 'ne'
        
        response = self.get_response(request)
        return response

