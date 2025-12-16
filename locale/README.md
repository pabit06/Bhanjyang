# Locale Directory

This directory contains translation files for internationalization (i18n) support.

## Structure

```
locale/
├── en/              # English translations
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── ne/              # Nepali (नेपाली) translations
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── README.md        # This file
```

## Supported Languages

- **English (en)** - Default language
- **Nepali (ne)** - नेपाली भाषा

## Generating Translation Files

### 1. Extract translatable strings:
```bash
python manage.py makemessages -l ne
python manage.py makemessages -l en
```

### 2. Edit translation files:
Edit the `.po` files in `locale/{language}/LC_MESSAGES/django.po`

### 3. Compile translations:
```bash
python manage.py compilemessages
```

## Usage in Templates

```django
{% load i18n %}
<h1>{% trans "Welcome" %}</h1>
<p>{% trans "This is a translated message" %}</p>
```

## Usage in Python Code

```python
from django.utils.translation import gettext as _

message = _("Welcome to Bhanjyang Cooperative")
```

## Adding New Languages

1. Create directory: `locale/{language_code}/LC_MESSAGES/`
2. Run: `python manage.py makemessages -l {language_code}`
3. Translate strings in the generated `.po` file
4. Compile: `python manage.py compilemessages`

