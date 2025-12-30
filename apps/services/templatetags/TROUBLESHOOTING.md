# Template Tag Troubleshooting

## Error: 'remittance_tags' is not a registered tag library

### Solution Steps:

1. **Restart Django Development Server** (REQUIRED)
   ```bash
   # Stop the server (Ctrl+C)
   # Then restart:
   python manage.py runserver
   ```

2. **Clear Python Cache** (if restart doesn't work)
   ```powershell
   # Windows PowerShell
   Get-ChildItem -Path "apps\services\templatetags\__pycache__" -Recurse | Remove-Item -Force -Recurse
   ```

3. **Verify Structure**
   ```
   apps/services/
   ├── templatetags/
   │   ├── __init__.py  (must exist, can be empty)
   │   └── remittance_tags.py
   ```

4. **Verify App is in INSTALLED_APPS**
   Check `config/settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'apps.services',  # Must be present
       ...
   ]
   ```

5. **Test Template Tag Library**
   ```bash
   python manage.py shell
   >>> from django.template import engines
   >>> 'remittance_tags' in engines['django'].engine.template_libraries
   # Should return True
   ```

### Why This Happens

Django discovers template tag libraries when:
- The server starts
- The app is in INSTALLED_APPS
- The templatetags directory exists with __init__.py

If you add a new template tag library while the server is running, you **must restart** the server for Django to discover it.

### Alternative: Remove Template Tag Usage (Temporary Fix)

If you can't restart the server right now, you can temporarily remove the template tag usage and use direct URLs:

```django
<!-- Instead of: -->
{% load remittance_tags %}
<img src="{% flag_image 'USD' %}">

<!-- Use: -->
<img src="https://flagcdn.com/w40/us.png">
```

But this is **not recommended** - restart the server instead!

