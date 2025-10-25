from django import template

register = template.Library()

@register.filter
def model_name(obj):
    """
    Get the model name of an object in lowercase
    Usage: {{ object|model_name }}
    """
    if obj is None:
        return ''
    return obj._meta.model_name.lower()
