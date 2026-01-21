from django import template
from django.utils.translation import get_language

register = template.Library()

NEP_DIGITS = {
    '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
    '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
}

@register.filter(name='to_nepali_digits')
def to_nepali_digits(value):
    """
    Converts English numerals to Nepali numerals if the current language is Nepali.
    """
    if get_language() != 'ne':
        return value
    
    value_str = str(value)
    return ''.join(NEP_DIGITS.get(char, char) for char in value_str)
