# Static Files Migration Guide

This document tracks the migration of static files to the new organized structure.

## Migration Status

### ✅ Completed Migrations

#### CSS Files
- ✅ `css/input.css` → `css/base/input.css`
- ✅ `css/gallery-advanced.css` → `css/pages/gallery-advanced.css`
- ✅ `css/gallery-lightbox.css` → `css/pages/gallery-lightbox.css`
- ✅ `css/animations.css` → `css/utilities/animations.css`
- ✅ `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
- ✅ `css/dark-mode.css` → `css/utilities/dark-mode.css`

#### JavaScript Files
- ✅ `js/gsap-init.js` → `js/base/gsap-init.js`
- ✅ `js/performance-monitor.js` → `js/base/performance-monitor.js`
- ✅ `js/gallery-advanced.js` → `js/pages/gallery-advanced.js`
- ✅ `js/gallery-lightbox.js` → `js/pages/gallery-lightbox.js`
- ✅ `js/animations.js` → `js/utilities/animations.js`
- ✅ `js/advanced-animations.js` → `js/utilities/advanced-animations.js`
- ✅ `js/dark-mode.js` → `js/utilities/dark-mode.js`
- ✅ `js/pwa-installer.js` → `js/utilities/pwa-installer.js`

#### Image Files
- ✅ `images/Logo.png` → `images/logos/Logo.png`
- ✅ `images/logo.svg` → `images/logos/logo.svg`
- ✅ `images/pattern-light.png` → `images/backgrounds/pattern-light.png`
- ✅ `images/hero*.jpg` → `images/heroes/`
- ✅ `images/hero*.png` → `images/heroes/`

### ✅ Updated References

#### Core Templates
- ✅ `templates/base.html` - Updated all CSS, JS, and image references
- ✅ `templates/partials/_header.html` - Updated logo path
- ✅ `templates/partials/_footer.html` - Updated logo path
- ✅ `templates/admin/base_site.html` - Updated logo paths
- ✅ `templates/admin/login.html` - Updated logo path
- ✅ `apps/services/templates/services/services.html` - Updated hero image paths

### ⚠️ Remaining Updates Needed

The following files still need their static file references updated:

#### Gallery Templates
- `apps/gallery/templates/gallery/gallery.html`
  - `css/gallery-advanced.css` → `css/pages/gallery-advanced.css`
  - `js/advanced-animations.js` → `js/utilities/advanced-animations.js`

- `apps/gallery/templates/gallery/album_detail.html`
  - `css/gallery-advanced.css` → `css/pages/gallery-advanced.css`
  - `js/gallery-advanced.js` → `js/pages/gallery-advanced.js`

- `apps/gallery/templates/gallery/analytics.html`
  - `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
  - `js/advanced-animations.js` → `js/utilities/advanced-animations.js`

- `apps/gallery/templates/gallery/smart_collections.html`
  - `css/gallery-lightbox.css` → `css/pages/gallery-lightbox.css`
  - `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
  - `js/advanced-animations.js` → `js/utilities/advanced-animations.js`

- `apps/gallery/templates/gallery/vr_gallery.html`
  - `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
  - `js/advanced-animations.js` → `js/utilities/advanced-animations.js`

#### Search Templates
- `apps/search/templates/search/advanced_search.html`
  - `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
  - `css/dark-mode.css` → `css/utilities/dark-mode.css`
  - `js/advanced-animations.js` → `js/utilities/advanced-animations.js`
  - `js/dark-mode.js` → `js/utilities/dark-mode.js`

#### Contact Templates
- `apps/contact/templates/contact/interactive_map.html`
  - `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
  - `css/dark-mode.css` → `css/utilities/dark-mode.css`
  - `css/gallery-lightbox.css` → `css/pages/gallery-lightbox.css`
  - `js/advanced-animations.js` → `js/utilities/advanced-animations.js`
  - `js/dark-mode.js` → `js/utilities/dark-mode.js`

#### Other Templates
- `templates/offline.html`
  - `css/advanced-animations.css` → `css/utilities/advanced-animations.css`
  - `css/dark-mode.css` → `css/utilities/dark-mode.css`
  - `js/dark-mode.js` → `js/utilities/dark-mode.js`

- `apps/about/templates/about/gallery.html`
  - `css/gallery-lightbox.css` → `css/pages/gallery-lightbox.css`
  - `js/gallery-lightbox.js` → `js/pages/gallery-lightbox.js`

## How to Update References

### Using Search and Replace

1. **Find all references:**
   ```bash
   grep -r "static 'css/advanced-animations.css'" .
   ```

2. **Update in your editor:**
   - Use find and replace
   - Old: `{% static 'css/advanced-animations.css' %}`
   - New: `{% static 'css/utilities/advanced-animations.css' %}`

### Path Mapping Reference

#### CSS Files
```
css/input.css → css/base/input.css
css/gallery-*.css → css/pages/gallery-*.css
css/animations.css → css/utilities/animations.css
css/advanced-animations.css → css/utilities/advanced-animations.css
css/dark-mode.css → css/utilities/dark-mode.css
```

#### JavaScript Files
```
js/gsap-init.js → js/base/gsap-init.js
js/performance-monitor.js → js/base/performance-monitor.js
js/gallery-*.js → js/pages/gallery-*.js
js/animations.js → js/utilities/animations.js
js/advanced-animations.js → js/utilities/advanced-animations.js
js/dark-mode.js → js/utilities/dark-mode.js
js/pwa-installer.js → js/utilities/pwa-installer.js
```

#### Image Files
```
images/Logo.png → images/logos/Logo.png
images/logo.svg → images/logos/logo.svg
images/pattern-light.png → images/backgrounds/pattern-light.png
images/hero*.jpg → images/heroes/hero*.jpg
images/hero*.png → images/heroes/hero*.png
```

## Testing After Migration

After updating references, test:

1. **Run development server:**
   ```bash
   python manage.py runserver
   ```

2. **Check browser console** for 404 errors

3. **Verify pages load correctly:**
   - Home page
   - Gallery pages
   - Contact page
   - Admin pages

4. **Check static files are served:**
   ```bash
   python manage.py collectstatic --dry-run
   ```

## Rollback Plan

If issues occur, you can rollback by:

1. Moving files back to original locations
2. Reverting template changes
3. Or using symlinks for backward compatibility

## Notes

- Some files like `css/about-animations.css` remain in root as they may be app-specific
- App-specific static files (e.g., `apps/gallery/static/`) are not affected
- The migration is gradual - you can update references as you work on each template

