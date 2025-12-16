# CSS Organization Guide

This directory contains all CSS files for the Bhanjyang Cooperative project.

## Structure

```
css/
├── base/                    # Base/reset styles
│   └── input.css           # Tailwind input (source)
├── components/              # Reusable component styles
│   ├── buttons.css
│   ├── cards.css
│   ├── forms.css
│   └── map-toggle.css
├── design-system/           # Design system tokens
│   ├── tokens.css
│   └── typography.css
├── pages/                   # Page-specific styles
│   ├── gallery-advanced.css
│   └── gallery-lightbox.css
├── utilities/               # Utility styles
│   ├── animations.css
│   ├── advanced-animations.css
│   └── dark-mode.css
└── dist/                    # Compiled output
    └── output.css
```

## File Categories

### Base Styles (`base/`)
- Foundation styles
- CSS reset/normalize
- Tailwind input files

### Components (`components/`)
- Reusable UI component styles
- Button styles
- Card styles
- Form styles
- Map toggle styles

### Design System (`design-system/`)
- Design tokens (colors, spacing, etc.)
- Typography definitions
- Theme variables

### Pages (`pages/`)
- Page-specific styles
- Gallery styles
- Member portal styles
- Other page-specific CSS

### Utilities (`utilities/`)
- Animation utilities
- Dark mode styles
- Helper classes

## Usage

### In Templates
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/base/input.css' %}">
<link rel="stylesheet" href="{% static 'css/components/buttons.css' %}">
<link rel="stylesheet" href="{% static 'css/pages/gallery-advanced.css' %}">
```

### Build Process
The main compiled CSS is in `dist/output.css` which includes Tailwind and custom styles.

## Adding New Styles

1. **Component styles** → `components/`
2. **Page-specific styles** → `pages/`
3. **Utility styles** → `utilities/`
4. **Design tokens** → `design-system/`

