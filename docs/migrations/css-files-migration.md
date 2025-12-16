# CSS Files Migration Details

## ✅ 6 CSS Files Moved

### 1. Base Styles (1 file)
- **`css/input.css`** → **`css/base/input.css`**
  - Tailwind CSS input file
  - Foundation/base styles

### 2. Page-Specific Styles (3 files)
- **`css/gallery-advanced.css`** → **`css/pages/gallery-advanced.css`**
  - Gallery page specific styles
  
- **`css/gallery-lightbox.css`** → **`css/pages/gallery-lightbox.css`**
  - Gallery lightbox styles
  

### 3. Utility Styles (3 files)
- **`css/animations.css`** → **`css/utilities/animations.css`**
  - Basic animation utilities
  
- **`css/advanced-animations.css`** → **`css/utilities/advanced-animations.css`**
  - Advanced animation utilities
  
- **`css/dark-mode.css`** → **`css/utilities/dark-mode.css`**
  - Dark mode styles

## 📊 Summary

| Category | Files | Old Location | New Location |
|----------|-------|--------------|--------------|
| Base | 1 | `css/` | `css/base/` |
| Pages | 2 | `css/` | `css/pages/` |
| Utilities | 3 | `css/` | `css/utilities/` |
| **Total** | **6** | | |

## 📁 Files NOT Moved (Remain in Original Location)

These files remain in their original locations:

- `css/components/buttons.css` - Already in components folder
- `css/components/cards.css` - Already in components folder
- `css/components/forms.css` - Already in components folder
- `css/components/map-toggle.css` - Already in components folder
- `css/design-system/tokens.css` - Already in design-system folder
- `css/design-system/typography.css` - Already in design-system folder
- `css/about-animations.css` - App-specific, remains in root
- `css/dist/output.css` - Compiled output, remains in dist folder

## 🔄 Path Updates in Templates

All template references have been updated:

### Before:
```django
{% static 'css/input.css' %}
{% static 'css/gallery-advanced.css' %}
{% static 'css/animations.css' %}
```

### After:
```django
{% static 'css/base/input.css' %}
{% static 'css/pages/gallery-advanced.css' %}
{% static 'css/utilities/animations.css' %}
```

## ✅ Status: COMPLETE

All 6 CSS files have been moved and all template references have been updated.

**Note:** `member-portal.css` was removed as it's no longer needed.

