from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def build_absolute_uri(request, path):
    """
    Build an absolute URI from a request and a path
    Usage: {{ request|build_absolute_uri:some_path }}
    """
    if not path:
        return ""
    
    if path.startswith('http'):
        return path
    
    return f"{request.scheme}://{request.get_host()}{path}"

@register.filter
def get_absolute_url(request, url):
    """
    Get absolute URL from a relative URL
    Usage: {{ relative_url|get_absolute_url:request }}
    """
    if not url:
        return ""
    
    if url.startswith('http'):
        return url
    
    return f"{request.scheme}://{request.get_host()}{url}"
