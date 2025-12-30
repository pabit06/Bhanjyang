# How to Enable the Template Tag

## Current Status
The template tag is **temporarily disabled** in `list.html` to allow the page to work immediately.

## To Enable the Template Tag:

1. **Restart Django Development Server**
   ```bash
   # Stop server (Ctrl+C)
   python manage.py runserver
   ```

2. **Uncomment the template tag load**
   In `apps/services/templates/services/remittance/list.html`, change:
   ```django
   {# {% load remittance_tags %} #} {# Temporarily disabled - restart server to enable #}
   ```
   To:
   ```django
   {% load remittance_tags %}
   ```

3. **Replace direct URLs with template tag**
   Replace all instances of:
   ```html
   <img src="https://flagcdn.com/w40/us.png" ...>
   ```
   With:
   ```html
   <img src="{% flag_image 'USD' %}" ...>
   ```

## Quick Find & Replace

Use these replacements:

- `https://flagcdn.com/w40/us.png` → `{% flag_image 'USD' %}`
- `https://flagcdn.com/w40/eu.png` → `{% flag_image 'EUR' %}`
- `https://flagcdn.com/w40/gb.png` → `{% flag_image 'GBP' %}`
- `https://flagcdn.com/w40/au.png` → `{% flag_image 'AUD' %}`
- `https://flagcdn.com/w40/ca.png` → `{% flag_image 'CAD' %}`
- `https://flagcdn.com/w40/jp.png` → `{% flag_image 'JPY' %}`
- `https://flagcdn.com/w40/in.png` → `{% flag_image 'INR' %}`
- `https://flagcdn.com/w40/ae.png` → `{% flag_image 'AED' %}`
- `https://flagcdn.com/w40/sa.png` → `{% flag_image 'SAR' %}`
- `https://flagcdn.com/w40/qa.png` → `{% flag_image 'QAR' %}`
- `https://flagcdn.com/w40/sg.png` → `{% flag_image 'SGD' %}`
- `https://flagcdn.com/w40/my.png` → `{% flag_image 'MYR' %}`
- `https://flagcdn.com/w40/th.png` → `{% flag_image 'THB' %}`
- `https://flagcdn.com/w40/np.png` → `{% flag_image 'NPR' %}`

## Why This Happened

Django caches template tag libraries when the server starts. Since `remittance_tags.py` was added after the server started, it wasn't discovered. After restarting, Django will automatically discover and register the template tag library.

