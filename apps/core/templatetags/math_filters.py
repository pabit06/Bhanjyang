from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_decimal(value):
    """Coerce a template value to Decimal, or None when it is not numeric."""
    if value is None or value == '':
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


@register.filter(name='mul')
def mul(value, arg):
    """
    Multiply two numbers.
    Usage: {{ stats.published_articles|mul:100 }}
    Returns '' when either side is not numeric, so it chains safely into
    floatformat the same way Django's own arithmetic filters do.
    """
    left, right = _to_decimal(value), _to_decimal(arg)
    if left is None or right is None:
        return ''
    return left * right


@register.filter(name='div')
def div(value, arg):
    """
    Divide one number by another.
    Usage: {{ total|div:count }}
    Returns '' for non-numeric input or division by zero.
    """
    left, right = _to_decimal(value), _to_decimal(arg)
    if left is None or right is None or right == 0:
        return ''
    return left / right


@register.filter(name='abs')
def absolute(value):
    """
    Absolute value, for showing a signed change without its sign
    (the arrow next to it already carries the direction).
    Usage: {{ metrics.events_change|abs }}
    """
    number = _to_decimal(value)
    if number is None:
        return ''
    return abs(number)
