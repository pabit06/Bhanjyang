# Static Files & Media Organization Guide

## 📁 **Django Static Files Best Practices**

This document outlines the proper organization of static files and media in the Bhanjyang Cooperative Django project.

### 🎯 **Static Files Structure**

```
static/
├── css/                           # Custom CSS files
│   ├── animations.css             # Animation styles
│   └── custom.css                 # Additional custom styles
├── js/                            # JavaScript files
│   ├── animations.js              # Animation scripts
│   ├── performance-monitor.js     # Performance monitoring
│   └── gsap-init.js              # GSAP initialization
├── images/                        # Global images
│   ├── default-news-placeholder.png
│   ├── hero_services_illustration.png
│   └── pattern-light.png
├── home/                          # App-specific static files
│   └── images/                   # Home app images
│       ├── Logo.png              # Main logo
│       ├── hero1.jpg             # Hero images
│       ├── hero2.jpg
│       ├── hero3.jpg
│       ├── slider4.jpg
│       ├── slider5.jpg
│       └── pattern-light.png
├── fonts/                         # Custom fonts
├── icons/                         # Icon files
├── vendor/                        # Third-party libraries
├── dist/                          # Compiled assets
│   └── output.css                # Tailwind CSS output
├── src/                           # Source files (for compilation)
│   └── input.css                 # Tailwind CSS input
├── robots.txt                     # SEO robots file
└── sitemap.xml                    # SEO sitemap
```

### 📱 **Media Files Structure**

```
media/
├── avatars/                       # User profile pictures
│   ├── 1.jpeg
│   ├── 2.jpg
│   ├── 3.jpg
│   └── ...
├── documents/                     # Document uploads
│   └── Kym_member.docx
├── gallery/                       # Image gallery
├── services/                      # Service-related images
│   └── relief/
│       └── medical_emergency_relief.png
└── news/                          # News article images
```

### 🔧 **Django Settings Configuration**

The project uses the following static file configuration:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 📋 **File Organization Rules**

#### **Static Files:**
1. **App-specific files** → `static/{app_name}/`
2. **Global files** → `static/`
3. **Compiled assets** → `static/dist/`
4. **Source files** → `static/src/`

#### **Media Files:**
1. **User uploads** → `media/`
2. **Organized by type** → `media/{type}/`
3. **Never commit to git** → Add to `.gitignore`

### 🚀 **Development Workflow**

#### **Adding New Static Files:**
1. Place files in appropriate `static/` subdirectory
2. Use `{% static 'path/to/file' %}` in templates
3. Run `python manage.py collectstatic` for production

#### **Adding New Media Files:**
1. Upload through Django admin or forms
2. Files automatically go to `media/` directory
3. Access via `{{ MEDIA_URL }}path/to/file`

### 📝 **Template Usage**

#### **Static Files:**
```html
{% load static %}
<link href="{% static 'css/custom.css' %}" rel="stylesheet">
<script src="{% static 'js/custom.js' %}"></script>
<img src="{% static 'main/images/Logo.png' %}" alt="Logo">
```

#### **Media Files:**
```html
<img src="{{ MEDIA_URL }}avatars/profile.jpg" alt="Profile">
<a href="{{ MEDIA_URL }}documents/file.pdf">Download</a>
```

### 🔍 **File Naming Conventions**

#### **Images:**
- Use descriptive names: `hero-services.jpg`
- Use PascalCase for logos: `Logo.png`
- Use lowercase for general images: `pattern-light.png`

#### **CSS/JS:**
- Use kebab-case: `performance-monitor.js`
- Use descriptive names: `animations.css`
- Group by functionality: `gsap-init.js`

#### **Media:**
- Use descriptive names: `member-photo-001.jpg`
- Include identifiers: `document-loan-application.pdf`
- Organize by date if needed: `2025-01-news-image.jpg`

### ⚡ **Performance Tips**

1. **Optimize Images:**
   - Use WebP format when possible
   - Compress images before upload
   - Use appropriate sizes for different devices

2. **Minify Assets:**
   - Minify CSS and JavaScript for production
   - Use Django's `collectstatic` with compression

3. **CDN Usage:**
   - Use CDN for external libraries
   - Consider CDN for static files in production

### 🛠️ **Maintenance Commands**

```bash
# Collect static files for production
python manage.py collectstatic

# Clear static files cache
python manage.py collectstatic --clear

# Check static files
python manage.py findstatic filename.css
```

### 📊 **File Size Guidelines**

- **Images:** Keep under 2MB for web use
- **Documents:** Keep under 10MB for uploads
- **CSS/JS:** Keep individual files under 100KB
- **Total static files:** Aim for under 5MB total

This organization ensures maintainability, performance, and follows Django best practices.
