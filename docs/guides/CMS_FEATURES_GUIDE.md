# Enterprise CMS Features Guide

## Overview

This guide explains how to use the enterprise-level content management features added to the home page content system.

## Table of Contents

1. [Status Management](#status-management)
2. [Preview/Draft System](#previewdraft-system)
3. [Scheduled Publishing](#scheduled-publishing)
4. [Content Versioning](#content-versioning)
5. [A/B Testing](#ab-testing)
6. [Bulk Operations](#bulk-operations)
7. [Media Management](#media-management)
8. [Cache Management](#cache-management)

---

## Status Management

### Available Statuses

- **Draft (DF)**: Content is not visible on the site
- **Published (PB)**: Content is live and visible
- **Scheduled (SC)**: Content will auto-publish at scheduled date
- **Archived (AR)**: Content is hidden but preserved

### How to Use

1. Go to Admin → Home → Home Page Content (or Testimonials, Statistics, Announcements)
2. Create or edit content
3. Select status from dropdown
4. For scheduled content, set `scheduled_date`
5. Save

**Note**: Only **Published** content appears on the live site.

---

## Preview/Draft System

### Previewing Draft Content

1. Create or edit content with status = **Draft**
2. Click **Preview** button in admin list
3. Preview page shows content with "PREVIEW MODE" banner
4. Only staff users can access preview

### Preview URL Format

```
/preview/<model_name>/<pk>/
```

Example: `/preview/homepagecontent/1/`

---

## Scheduled Publishing

### Setting Up Scheduled Content

1. Create content with status = **Scheduled**
2. Set `scheduled_date` to future date/time
3. Save
4. Content will auto-publish when scheduled date arrives

### How It Works

- Celery Beat runs every 5 minutes
- Checks for scheduled content with `scheduled_date <= now`
- Automatically changes status to **Published**
- Sets `published_date` to current time

### Manual Publishing

You can also manually publish scheduled content:
1. Select scheduled items
2. Use bulk action: **Publish selected items**

---

## Content Versioning

### Viewing Version History

1. Go to any content item in admin
2. Click **History** button (top right)
3. See all versions with timestamps
4. Click on any version to view details

### Comparing Versions

1. Go to version history
2. Select two versions
3. Click **Compare** to see differences
4. Changes are highlighted

### Rolling Back

1. View version history
2. Select the version you want to restore
3. Click **Revert to this version**
4. Confirm the action

---

## A/B Testing

### Creating Variants

1. Go to Admin → Home → Content Variants
2. Click **Add Content Variant**
3. Select content type and object
4. Enter variant name (e.g., "Variant A", "Variant B")
5. Add variant-specific data in JSON field
6. Activate variant

### Tracking Performance

- **Views**: Automatically tracked when variant is shown
- **Conversions**: Track manually or via API
- **Conversion Rate**: Calculated automatically

### Using Variants

```python
from apps.home.services import HomeService

# Track view
HomeService.track_variant_view(variant_id)

# Track conversion
HomeService.track_variant_conversion(variant_id)

# Get winning variant
winning = HomeService.get_winning_variant(content_type_id, object_id)
```

---

## Bulk Operations

### Available Bulk Actions

1. **Publish selected items**: Change status to Published
2. **Move selected to draft**: Change status to Draft
3. **Schedule selected items**: Change status to Scheduled
4. **Archive selected items**: Change status to Archived

### How to Use

1. Go to admin list page
2. Select items using checkboxes
3. Use **Select All** checkbox to select all items on page
4. Choose action from dropdown
5. Click **Go**
6. Confirm if prompted (for dangerous actions)

### Safety Features

- **Confirmation dialogs** for archive, draft, delete actions
- **Selected count** displayed before action
- **Warning messages** if no items selected

---

## Media Management

### Automatic Cleanup

- **django-cleanup** automatically manages media files
- When content is **deleted**, associated images/files are removed
- When content is **archived**, media files are **preserved**

### Best Practices

1. **Archive** instead of delete if you might need content later
2. Media files are automatically cleaned up on delete
3. No manual file management needed

---

## Cache Management

### Automatic Cache Clearing

Cache is automatically cleared when:
- Content is **published**
- Content is **updated** (if already published)
- Content is **deleted**

### Manual Cache Clearing

If needed, you can manually clear cache:

```python
from django.core.cache import cache

# Clear specific keys
cache.delete('home_context')
cache.delete('homepage_content')

# Clear all cache (if using Redis)
cache.clear()
```

### Cache Keys

- `home_context`: Full home page context
- `homepage_content`: Hero slides
- `featured_testimonials`: Testimonials
- `featured_statistics`: Statistics
- `featured_announcements`: Announcements
- `api_statistics`: Statistics API
- `api_testimonials`: Testimonials API

---

## Audit Trail

### What's Logged

All content operations are logged:
- **Publish**: Who published, when
- **Update**: Who updated published content, when
- **Archive**: Who archived, when
- **Bulk operations**: Who performed, how many items

### Viewing Logs

Logs are stored in Django's logging system. Check:
- Application logs
- Admin action history (via reversion)

### Audit Fields

- `published_by`: User who published
- `published_date`: When content was published
- `created_at`: When content was created
- `updated_at`: When content was last updated

---

## Tips & Best Practices

### 1. Workflow

1. Create content as **Draft**
2. Use **Preview** to check appearance
3. Set to **Scheduled** with future date
4. Or publish immediately as **Published**

### 2. Content Organization

- Use **order** field to control display sequence
- Use **is_featured** to highlight important content
- Archive old content instead of deleting

### 3. Performance

- Cache is automatically managed
- Only published content is cached
- Scheduled content doesn't affect cache until published

### 4. Safety

- Always preview before publishing
- Use confirmation dialogs for bulk operations
- Check version history before major changes
- Archive instead of delete when unsure

---

## Troubleshooting

### Content Not Showing on Site

1. Check status is **Published** (not Draft/Scheduled)
2. Check `scheduled_date` if Scheduled (must be in past)
3. Clear cache manually if needed
4. Check if content is featured (if required)

### Preview Not Working

1. Ensure you're logged in as staff user
2. Check content has been saved (has PK)
3. Verify URL is correct

### Scheduled Content Not Publishing

1. Check Celery Beat is running
2. Verify `scheduled_date` is in past
3. Check Celery logs for errors
4. Manually publish if needed

### Cache Not Clearing

1. Check signals are registered (in `apps.py`)
2. Verify cache backend is configured
3. Check logs for cache errors
4. Manually clear cache if needed

---

## API Reference

### Services

```python
from apps.home.services import HomeService

# Get content statistics
stats = HomeService.get_content_stats()

# Track A/B variant view
HomeService.track_variant_view(variant_id)

# Track A/B variant conversion
HomeService.track_variant_conversion(variant_id)

# Get winning variant
winning = HomeService.get_winning_variant(content_type_id, object_id)
```

### Models

```python
from apps.home.models import HomePageContent, Testimonial, Statistic, Announcement

# Check status
content.is_published  # True if Published
content.is_draft      # True if Draft
content.is_scheduled  # True if Scheduled

# Get preview URL
url = content.get_preview_url()
```

---

## Support

For issues or questions:
1. Check this guide first
2. Review admin interface
3. Check application logs
4. Contact development team

---

**Last Updated**: 2026-01-18
**Version**: 1.0
