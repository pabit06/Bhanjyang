from django import template

register = template.Library()


@register.filter
def build_absolute_uri(request, path):
    """
    Build an absolute URI from a request and a path.
    
    Usage: {{ request|build_absolute_uri:some_path }}
    
    Args:
        request: Django request object
        path: Relative or absolute path/URL
        
    Returns:
        Absolute URL string
    """
    if not path:
        return ""
    
    if path.startswith('http'):
        return path
    
    return f"{request.scheme}://{request.get_host()}{path}"
