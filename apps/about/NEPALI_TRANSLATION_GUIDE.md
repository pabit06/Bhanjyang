# About App - पूर्ण नेपाली Translation Guide

## 📋 Overview (अवलोकन)

यो document मा About App लाई पूर्ण नेपालीमा बनाउन आवश्यक सबै परिवर्तनहरूको सूची छ।

---

## ✅ Current Status (हालको अवस्था)

### Already Done (पहिले नै भएको):
- ✅ Models मा `gettext_lazy as _` use भएको छ
- ✅ Admin interface मा translation support छ
- ✅ Some fields मा Nepali versions छन्:
  - `cooperative_name_nepali`
  - `description_nepali`
  - `our_story_nepali`
- ✅ Django i18n setup भएको छ (`locale/` directory)
- ✅ Language settings मा Nepali (ne) support छ

### Needs Translation (अनुवाद चाहिने):
- ❌ Templates मा hardcoded English text
- ❌ Views मा hardcoded strings
- ❌ Services मा messages
- ❌ Default language setting (currently 'en-us')

---

## 🔧 Required Changes (आवश्यक परिवर्तनहरू)

### 1. **Settings Configuration (Settings मा परिवर्तन)**

**File:** `config/settings.py`

**Change:**
```python
# Current:
LANGUAGE_CODE = 'en-us'

# Change to:
LANGUAGE_CODE = 'ne'  # Nepali as default
```

**Also add (if not present):**
```python
MIDDLEWARE = [
    # ... other middleware ...
    'django.middleware.locale.LocaleMiddleware',  # Add this for language switching
    # ... other middleware ...
]
```

---

### 2. **Templates Translation (Templates मा अनुवाद)**

**Files to update (9 templates):**

#### 2.1 `introduction.html`
**Changes needed:**
- Add `{% load i18n %}` at top
- Translate all hardcoded text:
  - "Introduction" → "परिचय"
  - "Our Story, Vision & Journey" → "हाम्रो कथा, दृष्टिकोण र यात्रा"
  - "Our Story" → "हाम्रो कथा"
  - "Our Mission" → "हाम्रो उद्देश्य"
  - "Our Vision" → "हाम्रो दृष्टिकोण"
  - "Our Values" → "हाम्रो मूल्यहरू"
  - "Established" → "स्थापना"
  - "Registration" → "दर्ता"
  - "View Complete Timeline" → "पूर्ण टाइमलाइन हेर्नुहोस्"

**Example:**
```django
{% load i18n %}
{% load static %}

{% block title %}{% trans "Introduction" %} - Bhanjyang Cooperative{% endblock title %}

<!-- In template: -->
<span>{% trans "Introduction" %}</span>
<h1>{% trans "Our Story, Vision & Journey" %}</h1>
```

#### 2.2 `timeline.html`
**Changes:**
- "Timeline" → "टाइमलाइन"
- "Timeline Infographic" → "टाइमलाइन सूचना चित्र"
- "No Timeline Events" → "टाइमलाइन घटनाहरू छैनन्"

#### 2.3 `affiliations.html`
**Changes:**
- "Affiliations" → "सम्बन्धहरू"
- "Partnerships" → "साझेदारीहरू"

#### 2.4 `chairperson_message.html`
**Changes:**
- "Chairperson Message" → "अध्यक्षको सन्देश"
- "Back to About Us" → "हाम्रो बारेमा फर्कनुहोस्"

#### 2.5 `manager_commitment.html`
**Changes:**
- "Manager Commitment" → "प्रबन्धकको प्रतिबद्धता"
- "Back to About Us" → "हाम्रो बारेमा फर्कनुहोस्"

#### 2.6 `board_of_directors.html`
**Changes:**
- "Board of Directors" → "सञ्चालक समिति"
- "Back to About Us" → "हाम्रो बारेमा फर्कनुहोस्"

#### 2.7 `management.html`
**Changes:**
- "Management" → "प्रबन्धन"
- "Back to About Us" → "हाम्रो बारेमा फर्कनुहोस्"

#### 2.8 `member_testimonials.html`
**Changes:**
- "Member Testimonials" → "सदस्यहरूको प्रशंसा"
- "Back to About Us" → "हाम्रो बारेमा फर्कनुहोस्"

#### 2.9 `cooperative_detail.html`
**Changes:**
- "About" → "बारेमा"
- "Mission" → "उद्देश्य"
- "Vision" → "दृष्टिकोण"
- "Values" → "मूल्यहरू"
- "Cooperative Details" → "सहकारी विवरण"
- "Established" → "स्थापना"
- "Registration Number" → "दर्ता नम्बर"
- "License Number" → "इजाजतपत्र नम्बर"
- "Contact Information" → "सम्पर्क जानकारी"
- "Address" → "ठेगाना"
- "Phone" → "फोन"
- "Email" → "इमेल"

---

### 3. **Use Nepali Fields in Templates (Nepali fields use गर्ने)**

**Priority:** High - यो important छ!

**Files to update:**
- `introduction.html`
- `cooperative_detail.html`

**Logic to add:**
```django
{# Use Nepali name if available, else English #}
{% if cooperative_info.cooperative_name_nepali %}
    {{ cooperative_info.cooperative_name_nepali }}
{% else %}
    {{ cooperative_info.cooperative_name }}
{% endif %}

{# Use Nepali description if available #}
{% if cooperative_info.description_nepali %}
    {{ cooperative_info.description_nepali }}
{% else %}
    {{ cooperative_info.description }}
{% endif %}

{# Use Nepali our_story if available #}
{% if cooperative_info.our_story_nepali %}
    {{ cooperative_info.our_story_nepali }}
{% else %}
    {{ cooperative_info.our_story }}
{% endif %}
```

---

### 4. **Views Translation (Views मा अनुवाद)**

**File:** `apps/about/views.py`

**Changes:**
```python
from django.utils.translation import gettext_lazy as _

# In docstrings and any hardcoded strings:
class IntroductionView(SafeContextDataMixin, TemplateView):
    """{% trans "Introduction page with Our Story, Vision & Mission, and Timeline" %}"""
    # ...
```

**Note:** Views मा ज्यादा hardcoded text छैन, तर docstrings translate गर्न सकिन्छ।

---

### 5. **Services Translation (Services मा अनुवाद)**

**File:** `apps/about/services.py`

**Check for:**
- Error messages
- Log messages
- Any user-facing text

**Example:**
```python
from django.utils.translation import gettext as _

logger.error(_("Unable to load cooperative information"))
```

---

### 6. **Generate Translation Files (Translation files generate गर्ने)**

**Steps:**

1. **Extract translatable strings:**
```bash
python manage.py makemessages -l ne
python manage.py makemessages -l en
```

2. **Edit translation files:**
   - Open `locale/ne/LC_MESSAGES/django.po`
   - Translate all English strings to Nepali

3. **Compile translations:**
```bash
python manage.py compilemessages
```

---

### 7. **URL Patterns (Optional - Language Prefix)**

**If you want language prefix in URLs:**
- `/ne/about/introduction/` (Nepali)
- `/en/about/introduction/` (English)

**File:** `config/urls.py`

**Add:**
```python
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # ... other patterns ...
] + i18n_patterns(
    path('about/', include('apps.about.urls')),
    # ... other app URLs ...
    prefix_default_language=False,  # Don't show prefix for default language
)
```

---

## 📝 Implementation Checklist (कार्यान्वयन सूची)

### Phase 1: Basic Setup
- [ ] Change `LANGUAGE_CODE` to 'ne' in settings.py
- [ ] Add `LocaleMiddleware` to MIDDLEWARE (if not present)
- [ ] Add `{% load i18n %}` to all templates

### Phase 2: Template Translation
- [ ] Translate `introduction.html`
- [ ] Translate `timeline.html`
- [ ] Translate `affiliations.html`
- [ ] Translate `chairperson_message.html`
- [ ] Translate `manager_commitment.html`
- [ ] Translate `board_of_directors.html`
- [ ] Translate `management.html`
- [ ] Translate `member_testimonials.html`
- [ ] Translate `cooperative_detail.html`

### Phase 3: Use Nepali Fields
- [ ] Update `introduction.html` to use `cooperative_name_nepali`
- [ ] Update `introduction.html` to use `description_nepali`
- [ ] Update `introduction.html` to use `our_story_nepali`
- [ ] Update `cooperative_detail.html` to use Nepali fields

### Phase 4: Generate Translations
- [ ] Run `makemessages -l ne`
- [ ] Translate all strings in `django.po`
- [ ] Run `compilemessages`
- [ ] Test translations

### Phase 5: Testing
- [ ] Test all pages in Nepali
- [ ] Verify Nepali fields display correctly
- [ ] Check language switching (if implemented)
- [ ] Test admin interface in Nepali

---

## 🎯 Priority Order (प्राथमिकता क्रम)

1. **High Priority:**
   - Change default language to Nepali
   - Use Nepali fields in templates (cooperative_name_nepali, etc.)
   - Translate main templates (introduction.html, cooperative_detail.html)

2. **Medium Priority:**
   - Translate all other templates
   - Generate and fill translation files

3. **Low Priority:**
   - Language prefix in URLs
   - Language switcher UI

---

## 📚 Resources (स्रोतहरू)

- Django i18n Documentation: https://docs.djangoproject.com/en/5.2/topics/i18n/
- Translation files location: `locale/ne/LC_MESSAGES/django.po`
- Template translation: `{% trans "text" %}` or `{% blocktrans %}...{% endblocktrans %}`

---

## ⚠️ Important Notes (महत्वपूर्ण नोटहरू)

1. **Nepali Fields Priority:**
   - Always check if Nepali field exists before using English
   - Use fallback logic: `{% if nepali_field %}{{ nepali_field }}{% else %}{{ english_field }}{% endif %}`

2. **Translation Context:**
   - Some words may need context (e.g., "About" can mean "बारेमा" or "लगभग")
   - Use `{% trans "text" context "context_name" %}` if needed

3. **Date Formatting:**
   - Nepali dates may need different formatting
   - Use `{% language 'ne' %}` block for date formatting

4. **Testing:**
   - Always test with actual Nepali content
   - Check font rendering for Nepali characters
   - Verify all special characters display correctly

---

## 🚀 Quick Start (छिटो सुरुवात)

```bash
# 1. Change default language
# Edit config/settings.py: LANGUAGE_CODE = 'ne'

# 2. Add i18n to templates
# Add {% load i18n %} to each template

# 3. Generate translation files
python manage.py makemessages -l ne

# 4. Translate strings in locale/ne/LC_MESSAGES/django.po

# 5. Compile translations
python manage.py compilemessages

# 6. Restart server
python manage.py runserver
```

---

**Last Updated:** 2024
**Status:** Ready for Implementation

