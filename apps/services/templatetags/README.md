# Template Tags for Services App

## remittance_tags

Template tag library for remittance services functionality.

### Available Tags

#### `flag_image`
Returns the URL for a currency flag image. Prefers local static files, falls back to flagcdn.com.

**Usage:**
```django
{% load remittance_tags %}
<img src="{% flag_image 'USD' %}" alt="USD flag">
```

**Parameters:**
- `currency_code` (required): ISO currency code (e.g., 'USD', 'EUR', 'GBP')
- `size` (optional): Image size, defaults to 'w40'

**Example:**
```django
{% flag_image 'USD' %}
{% flag_image 'EUR' 'w80' %}
```

#### `flag_image_local`
Returns the local static path to a flag image (assumes flags are downloaded).

**Usage:**
```django
{% load remittance_tags %}
<img src="{% flag_image_local 'USD' %}" alt="USD flag">
```

## Installation

The template tag library is automatically discovered by Django when:
1. The `templatetags` directory exists in the app
2. The `__init__.py` file exists (making it a Python package)
3. The app is in `INSTALLED_APPS`
4. **The Django server is restarted** (important!)

## Troubleshooting

If you get `'remittance_tags' is not a registered tag library`:

1. **Restart the Django development server** - This is the most common issue
2. Verify the structure:
   ```
   apps/services/
   ├── templatetags/
   │   ├── __init__.py
   │   └── remittance_tags.py
   ```
3. Check that `apps.services` is in `INSTALLED_APPS`
4. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`

## Testing

To test if the template tag library is working:

```python
python manage.py shell
>>> from django.template import engines
>>> engines['django'].engine.template_libraries.keys()
# Should include 'remittance_tags'
```

