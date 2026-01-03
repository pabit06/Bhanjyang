# Nepali Datepicker Integration Guide

## Overview
Nepali Datepicker v5.0.6 has been integrated into the project for project-wide use. This allows users to select dates in Nepali calendar format throughout the application.

## Files Location
- **CSS**: `static/vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.css`
- **JavaScript**: `static/vendor/nepali-datepicker/nepali.datepicker.v5.0.6.min.js`
- **Initialization Script**: `static/js/vendor/nepali-datepicker-init.js`
- **Widget**: `apps/core/widgets.py`

## Usage

### 1. Using Django Widget (Recommended)

#### For Date Fields:
```python
from apps.core.widgets import NepaliDateInput

class MyForm(forms.Form):
    date_field = forms.DateField(
        widget=NepaliDateInput(attrs={'class': 'form-control'})
    )
```

#### For DateTime Fields:
```python
from apps.core.widgets import NepaliDateTimeInput

class MyForm(forms.Form):
    datetime_field = forms.DateTimeField(
        widget=NepaliDateTimeInput(attrs={'class': 'form-control'})
    )
```

#### For Date Range:
```python
from apps.core.widgets import NepaliDateRangeInput

class MyForm(forms.Form):
    date_range = forms.CharField(
        widget=NepaliDateRangeInput(attrs={'class': 'form-control'})
    )
```

### 2. Using in Templates (Manual)

Add the class `nepali-datepicker` to any input field:

```html
<input type="text" class="nepali-datepicker form-control" id="my-date" />
```

For date range:
```html
<input type="text" class="nepali-datepicker-range form-control" id="my-date-range" />
```

### 3. Programmatic Initialization

If you need to initialize datepicker on dynamically added elements:

```javascript
// Initialize a single element
window.initNepaliDatepicker(document.getElementById('my-date'));

// Or use the exported function
NepaliDatepickerInit.initElement(document.getElementById('my-date'));
```

## Current Implementation

The following forms have been updated to use Nepali Datepicker:

1. **News & Events Forms** (`apps/news_events/forms.py`):
   - `EventForm`: `event_date`, `end_date`, `registration_deadline`
   - `NewsArticleForm`: `published_date`, `scheduled_date`

2. **Contact Forms** (`apps/contact/forms.py`):
   - `KYMForm`: `dob` (Date of Birth)

## Features

- **Automatic Initialization**: All inputs with class `nepali-datepicker` are automatically initialized
- **Date Format**: Uses `YYYY-MM-DD` format
- **Language**: Nepali calendar with English date support
- **Read-only Input**: Prevents manual typing, ensures data consistency
- **Form Integration**: Automatically triggers change events for form validation

## Customization

To customize the datepicker behavior, modify the initialization in `static/js/vendor/nepali-datepicker-init.js`:

```javascript
input.NepaliDatePicker({
    dateFormat: "YYYY-MM-DD",
    language: "nepali",
    ndpYear: true,
    ndpMonth: true,
    ndpYearCount: 10,
    // Add more options as needed
});
```

## Adding to New Forms

1. Import the widget:
   ```python
   from apps.core.widgets import NepaliDateInput
   ```

2. Use in form field:
   ```python
   my_date = forms.DateField(
       widget=NepaliDateInput(attrs={'class': 'form-control'})
   )
   ```

3. The CSS and JS are automatically included via base template.

## Notes

- The datepicker is loaded globally in `templates/base.html`
- All date inputs with the appropriate class are automatically initialized
- The widget handles date conversion between Nepali and English calendars
- For datetime fields, use `NepaliDateTimeInput` widget

