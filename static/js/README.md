# JavaScript Organization Guide

This directory contains all JavaScript files for the Bhanjyang Cooperative project.

## Structure

```
js/
├── base/                    # Base/core scripts
│   ├── gsap-init.js        # GSAP initialization
│   └── performance-monitor.js
├── components/              # Reusable components
│   ├── cards/
│   │   └── StatCard.js
│   ├── feedback/
│   │   ├── Modal.js
│   │   └── Toast.js
│   ├── forms/
│   │   ├── FileUpload.js
│   │   └── FormField.js
│   ├── Component.js
│   └── index.js
├── pages/                   # Page-specific scripts
│   ├── gallery-advanced.js
│   └── gallery-lightbox.js
├── utilities/               # Utility scripts
│   ├── animations.js
│   ├── advanced-animations.js
│   ├── dark-mode.js
│   └── pwa-installer.js
└── vendor/                  # Third-party libraries
```

## File Categories

### Base Scripts (`base/`)
- Core initialization
- Performance monitoring
- GSAP setup
- Global utilities

### Components (`components/`)
- Reusable UI components
- StatCard component
- Modal component
- Toast notifications
- Form components
- Component index for exports

### Pages (`pages/`)
- Page-specific functionality
- Gallery scripts
- Member portal scripts
- Other page-specific JS

### Utilities (`utilities/`)
- Animation utilities
- Dark mode toggle
- PWA installer
- Helper functions

### Vendor (`vendor/`)
- Third-party libraries
- External dependencies

## Usage

### In Templates
```django
{% load static %}
<script src="{% static 'js/base/gsap-init.js' %}"></script>
<script src="{% static 'js/components/index.js' %}"></script>
<script src="{% static 'js/pages/gallery-advanced.js' %}"></script>
```

### Component Usage
```javascript
// Import from components
import { Modal, Toast } from './components/index.js';
```

## Adding New Scripts

1. **Component scripts** → `components/`
2. **Page-specific scripts** → `pages/`
3. **Utility scripts** → `utilities/`
4. **Third-party libraries** → `vendor/`

## Best Practices

- Keep components modular and reusable
- Use ES6 modules for better organization
- Document complex functions
- Follow naming conventions (PascalCase for components, camelCase for functions)

