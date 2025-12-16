# Images Organization Guide

This directory contains all image assets for the Bhanjyang Cooperative project.

## Structure

```
images/
├── icons/                   # Icon files
├── logos/                   # Logo files
│   ├── Logo.png
│   └── logo.svg
├── backgrounds/             # Background images
│   └── pattern-light.png
├── heroes/                  # Hero section images
│   ├── hero1.jpg
│   ├── hero2.jpg
│   ├── hero3.jpg
│   ├── slider4.jpg
│   ├── slider5.jpg
│   ├── hero_services_illustration.png
│   ├── hero-contact.png
│   ├── hero-download-image.png
│   └── Hero-download.png
├── remit_logos/            # Remittance service logos
│   ├── cityexpress.jpg
│   ├── esewa.png
│   ├── himalremit.png
│   ├── ime.png
│   ├── imepay.png
│   ├── khalti.png
│   └── westernunion.png
├── default-news-placeholder.png
├── Download-hero-image.png
└── plant-illustration.png
```

## File Categories

### Icons (`icons/`)
- Small icon files
- SVG icons preferred
- PNG icons for fallback

### Logos (`logos/`)
- Company logos
- Partner logos
- Brand assets

### Backgrounds (`backgrounds/`)
- Pattern images
- Background textures
- Decorative elements

### Heroes (`heroes/`)
- Hero section images
- Slider images
- Main banner images

### Remit Logos (`remit_logos/`)
- Remittance service provider logos
- Payment gateway logos

## Usage

### In Templates
```django
{% load static %}
<img src="{% static 'images/logos/Logo.png' %}" alt="Logo">
<img src="{% static 'images/heroes/hero1.jpg' %}" alt="Hero">
```

### In CSS
```css
.hero-section {
    background-image: url('/static/images/heroes/hero1.jpg');
}
```

## Image Guidelines

1. **Format:**
   - Photos: JPG
   - Logos/Icons: PNG or SVG
   - Simple graphics: SVG preferred

2. **Optimization:**
   - Compress images before upload
   - Use appropriate dimensions
   - Consider WebP for modern browsers

3. **Naming:**
   - Use lowercase with hyphens
   - Be descriptive
   - Include size if multiple versions exist

4. **Organization:**
   - Group related images in subdirectories
   - Keep root level minimal
   - Use descriptive folder names

## Adding New Images

1. **Icons** → `icons/`
2. **Logos** → `logos/`
3. **Backgrounds** → `backgrounds/`
4. **Hero images** → `heroes/`
5. **Service-specific** → Create subdirectory (e.g., `remit_logos/`)

