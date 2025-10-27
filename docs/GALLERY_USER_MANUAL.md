# Gallery App - Complete User Manual

**Version**: 2.0  
**Last Updated**: Today  
**Status**: Production Ready

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Overview](#overview)
3. [User Guide](#user-guide)
4. [Admin Guide](#admin-guide)
5. [Developer Guide](#developer-guide)
6. [API Documentation](#api-documentation)
7. [Features & Capabilities](#features--capabilities)
8. [Workflows](#workflows)
9. [Troubleshooting](#troubleshooting)
10. [Appendix](#appendix)

---

## Introduction

### What is the Gallery App?

The Gallery App is a comprehensive image management and display system for the Bhanjyang Cooperative website. It provides a beautiful, responsive gallery interface for showcasing events, team activities, office life, community work, and awards.

### Key Features

- 📸 **Image Management** - Upload, organize, and manage gallery images
- 🎨 **Beautiful Display** - Responsive masonry grid with lightbox
- 🔍 **Smart Search** - Search by title, description, and AI-generated tags
- 🏷️ **Categorization** - Organize images by events, team, office, community, awards
- 📂 **Albums** - Create nested album structures
- ❤️ **Social Features** - Like, share, and comment on images
- 📊 **Analytics** - Track views, likes, shares, and downloads
- 🤖 **AI Features** - Auto-tagging, sentiment analysis, quality scoring
- 🔄 **Smart Collections** - Automatically curated image collections
- 📱 **Mobile Optimized** - Responsive design with mobile image versions

---

## Overview

### Architecture

```
Gallery App Components:
├── Models (Data Layer)
│   ├── GalleryAlbum - Album organization
│   ├── GalleryImage - Image storage and metadata
│   ├── GalleryImageLike - Like tracking
│   ├── GalleryImageComment - Comment management
│   ├── GalleryImageShare - Share tracking
│   ├── GalleryImageDownload - Download tracking
│   ├── SmartCollection - Auto-curated collections
│   ├── SmartCollectionImage - Collection relationships
│   ├── AutoCategorizationRule - Auto-categorization rules
│   └── ImageAnalysisJob - Background AI processing
│
├── Views (Presentation Layer)
│   ├── Template Views - HTML page rendering
│   └── API Views - JSON data endpoints
│
├── Admin (Management Layer)
│   ├── Gallery Album Admin
│   ├── Gallery Image Admin
│   ├── Tracking Admins (Like, Comment, Share, Download)
│   └── Smart Collection Admins
│
└── Templates (Frontend)
    ├── gallery/gallery.html - Main gallery view
    └── Admin templates
```

### Data Models

#### GalleryAlbum
```python
Fields:
- name: Album name
- description: Album description
- cover_image: Album cover image
- parent_album: Parent album (for nesting)
- is_featured: Show on homepage
- is_active: Published status
- order: Display order
- created_at, updated_at: Timestamps

Key Methods:
- get_path() - Get full album path
- get_image_count() - Get active image count
- get_sub_album_count() - Get sub-album count
```

#### GalleryImage
```python
Fields:
- title: Image title
- description: Image description
- image: Image file (JPG, PNG, WEBP)
- album: Parent album
- category: Category (events, team, office, community, awards)
- is_featured: Show on homepage
- is_active: Published status
- order: Display order

AI Fields:
- ai_tags: AI-generated tags
- ai_description: AI-generated description
- ai_color_palette: Detected colors
- ai_objects: Detected objects
- ai_scene_type: Scene classification
- ai_sentiment: Sentiment analysis
- ai_quality_score: Quality score (0-1)

Social Fields:
- likes_count, shares_count, views_count, comments_count
- is_public, allow_comments, allow_downloads

Key Methods:
- get_thumbnail_url() - Get thumbnail URL
- get_mobile_image_url() - Get mobile-optimized version
- get_image_dimensions() - Get image dimensions
- get_file_size_mb() - Get file size in MB
```

---

## User Guide

### For End Users

#### Viewing the Gallery

**Access**: Navigate to `/gallery/` on the website

**Features Available**:
- 🖼️ Browse images in a beautiful masonry grid
- 🔍 Search images by keywords
- 📂 Filter by albums
- 🏷️ Filter by categories
- ⭐ View featured content
- 👁️ Click images for lightbox view
- ❤️ Like images
- 📤 Share images
- 💬 Comment on images
- ⬇️ Download images (if allowed)

#### Using the Gallery

1. **Browse Images**
   - Scroll through the grid to see all images
   - Click on any image to open it in a lightbox
   - Navigate between images using arrow keys or buttons
   - Close the lightbox by clicking outside or pressing ESC

2. **Search Images**
   - Use the search bar at the top
   - Search by:
     - Image title
     - Image description
     - AI-generated tags
   - Results update in real-time

3. **Filter Images**
   - **By Album**: Click on an album card
   - **By Category**: Use category filters
   - **Featured**: View only featured content

4. **Interact with Images**
   - **Like**: Click the heart icon ❤️
   - **Share**: Click the share button (multiple platforms)
   - **Comment**: Add comments (requires approval)
   - **Download**: Click download (if enabled)

5. **View Album Details**
   - Click on an album card
   - See all images in that album
   - View album description
   - Navigate back to all galleries

#### Mobile Experience

- Responsive design adapts to your screen
- Mobile-optimized images load automatically
- Touch-friendly controls
- Swipe navigation in lightbox

---

## Admin Guide

### For Content Managers

#### Accessing the Admin

1. Log in at `/admin/`
2. Navigate to **Gallery** section
3. Manage albums, images, and collections

#### Managing Albums

**Create an Album**:
1. Go to **Gallery** → **Albums** → **Add Album**
2. Enter:
   - **Name**: Album name (e.g., "Annual Event 2024")
   - **Description**: Brief description
   - **Cover Image**: Optional cover image
   - **Parent Album**: Create nested albums
   - **Featured**: Check to show on homepage
   - **Active**: Check to publish
   - **Order**: Display order (lower numbers first)
3. Click **Save**

**Edit an Album**:
1. Find the album in the list
2. Click on the album name
3. Modify fields as needed
4. Click **Save**

**Delete an Album**:
1. Select the album
2. Choose "Delete" from actions
3. Confirm deletion

#### Managing Images

**Upload Images**:

*Single Upload*:
1. Go to **Gallery** → **Images** → **Add Image**
2. Enter:
   - **Title**: Image title
   - **Description**: Image description
   - **Image**: Choose image file
   - **Album**: Select album (optional)
   - **Category**: Choose category
   - **Featured**: Check to show on homepage
   - **Active**: Check to publish
3. Click **Save**

*Bulk Upload*:
1. Click **"Bulk Upload Images"** button
2. Select multiple images
3. Choose album and category
4. Click **Upload**
5. Images are uploaded with auto-generated titles

**Edit Images**:
1. Find the image in the list (visible thumbnails)
2. Click on the image title
3. Modify fields
4. View thumbnail in right panel
5. Click **Save**

**Delete Images**:
1. Select images using checkboxes
2. Choose "Delete selected images" from actions
3. Confirm deletion

#### Advanced Admin Features

**Image Actions**:
- Mark as featured/unfeatured
- Mark as active/inactive
- Optimize images
- Optimize for mobile
- Generate thumbnails
- Assign to album

**Batch Operations**:
1. Select multiple images using checkboxes
2. Choose an action:
   - Assign to album
   - Set category
   - Toggle featured status
   - Toggle active status
   - Optimize images
   - Delete images
3. Click **Go**

#### Using Smart Collections

**What are Smart Collections?**

Smart Collections automatically gather images based on rules like:
- Keywords in title/description
- Specific albums
- Categories
- AI sentiment
- Quality scores

**Create a Smart Collection**:
1. Go to **Gallery** → **Smart Collections** → **Add Collection**
2. Enter:
   - **Name**: Collection name
   - **Description**: Description
   - **Match Type**: Match ALL rules or ANY rule
   - **Keywords**: Comma-separated keywords
   - **Album**: Specific album
   - **Category**: Specific category
   - **Min Quality Score**: 0.0-1.0
   - **AI Sentiment**: Specific sentiment
3. Click **Save**

**Update Collections**:
1. Select collections
2. Choose "Update Collections" action
3. Collection is automatically updated with matching images

#### Viewing Analytics

**View Image Stats**:
1. Go to **Gallery** → **Images**
2. Each image shows:
   - Views count
   - Likes count
   - Created date

**Track Detailed Analytics**:
1. Go to **Gallery** → **Analytics**
2. View:
   - Total views, likes, shares, downloads
   - Category distribution
   - Top performing images
   - Recent activity

**Track Likes**:
1. Go to **Gallery** → **Likes**
2. See who liked which images
3. View by IP, session, date

**Track Shares**:
1. Go to **Gallery** → **Shares**
2. See sharing activity
3. Filter by platform

**Track Downloads**:
1. Go to **Gallery** → **Downloads**
2. See download activity
3. Track original vs. thumbnail downloads

#### Managing Comments

**Moderate Comments**:
1. Go to **Gallery** → **Comments**
2. Review pending comments
3. Approve or reject comments
4. Edit comments if needed

---

## Developer Guide

### For Developers

#### Project Structure

```
gallery/
├── models.py          # Database models
├── views.py           # View logic
├── admin.py           # Admin configuration
├── urls.py            # URL routing
├── apps.py            # App configuration
├── migrations/        # Database migrations
├── templates/         # HTML templates
│   └── gallery/
│       ├── gallery.html      # Main gallery view
│       ├── album_detail.html # Album detail view
│       ├── analytics.html    # Analytics dashboard
│       ├── vr_gallery.html   # VR gallery view
│       └── admin/            # Admin templates
└── static/            # Static files (if any)
```

#### Key Files

**models.py**:
- Defines all database models
- Includes validation functions
- Contains helper methods

**views.py**:
- Template views (HTML rendering)
- API views (JSON responses)
- Analytics tracking
- Image processing

**admin.py**:
- Admin interface configuration
- Custom actions
- Bulk operations
- Field display customization

#### Adding New Features

**Add a New Category**:

1. Update `models.py`:
```python
# GalleryImage.CATEGORY_CHOICES
category = models.CharField(
    max_length=20,
    choices=[
        ('events', 'Events'),
        ('team', 'Team'),
        ('office', 'Office'),
        ('community', 'Community'),
        ('awards', 'Awards'),
        ('new_category', 'New Category'),  # Add this
    ],
    default='events'
)
```

2. Create migration:
```bash
python manage.py makemigrations gallery
python manage.py migrate gallery
```

3. Update admin filters if needed

**Add a New Field**:

1. Add field to model in `models.py`
2. Add to admin in `admin.py`
3. Create and apply migration
4. Update template if displaying field

#### Customization

**Change Gallery Layout**:

Edit `gallery/templates/gallery/gallery.html`:
- Modify grid layout
- Change lightbox behavior
- Customize filters
- Add custom CSS/JS

**Modify Search Behavior**:

Edit `gallery/views.py` → `gallery_search_api`:
```python
images = GalleryImage.objects.filter(
    is_active=True
).filter(
    Q(title__icontains=query) | 
    Q(description__icontains=query) |
    Q(ai_tags__icontains=query) |
    Q(custom_field__icontains=query)  # Add custom fields
)
```

**Custom Admin Actions**:

Add to `gallery/admin.py`:
```python
class GalleryImageAdmin(admin.ModelAdmin):
    actions = [existing_actions, 'custom_action']
    
    def custom_action(self, request, queryset):
        # Your custom logic
        pass
    custom_action.short_description = "Custom Action"
```

#### Performance Tips

1. **Use Indexes**: Already implemented, don't remove
2. **Prefetch Related**: Used in views for efficiency
3. **Cache Results**: Enable caching for frequently accessed data
4. **Optimize Images**: Use provided optimization tools
5. **Monitor Queries**: Use Django Debug Toolbar

---

## API Documentation

### Public Endpoints

#### Get Gallery Images
```http
GET /gallery/api/images/
```

**Query Parameters**:
- `album_id`: Filter by album ID
- `category`: Filter by category
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)

**Response**:
```json
{
  "success": true,
  "images": [
    {
      "id": 1,
      "title": "Image Title",
      "description": "Image description",
      "image_url": "/media/gallery/image.jpg",
      "thumbnail_url": "/media/gallery/image_thumb.jpg",
      "album_name": "Album Name",
      "album_id": 1,
      "category": "events",
      "category_name": "Events",
      "ai_tags": ["tag1", "tag2"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "has_next": true,
    "has_previous": false,
    "page_number": 1,
    "total_pages": 10,
    "total_images": 200
  }
}
```

#### Search Gallery
```http
GET /gallery/api/search/?query=keyword
```

**Query Parameters**:
- `query`: Search keyword (required)

**Response**:
```json
{
  "success": true,
  "images": [...]  // Array of matching images
}
```

#### Get Albums
```http
GET /gallery/api/albums/
```

**Response**:
```json
{
  "success": true,
  "albums": [
    {
      "id": 1,
      "name": "Album Name",
      "description": "Album description",
      "cover_image": "/media/gallery/albums/cover.jpg",
      "image_count": 25,
      "sub_album_count": 3,
      "parent_album": null,
      "is_featured": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Categories
```http
GET /gallery/api/categories/
```

**Response**:
```json
{
  "success": true,
  "categories": [
    {
      "key": "events",
      "name": "Events",
      "count": 50
    }
  ]
}
```

#### Track Analytics
```http
POST /gallery/api/analytics/
Content-Type: application/json
```

**Request Body**:
```json
{
  "image_id": 1,
  "action": "view|like|share|download"
}
```

**Actions**:
- `view`: Track page view
- `like`: Like/unlike image (toggle)
- `share`: Track share (include `platform` field)
- `download`: Track download

**Response**:
```json
{
  "success": true,
  "message": "Action recorded",
  "view_count": 150,
  "like_count": 25,
  "share_count": 10
}
```

### Staff-Only Endpoints

#### Update Smart Collection
```http
POST /gallery/api/smart-collections/{id}/update/
```

**Authentication**: Staff required

**Response**:
```json
{
  "success": true,
  "message": "Collection updated",
  "image_count": 15
}
```

#### Apply Auto-Categorization
```http
POST /gallery/api/auto-categorization/apply/
```

**Authentication**: Staff required

**Response**:
```json
{
  "success": true,
  "message": "Rules applied",
  "applied_count": 42
}
```

---

## Features & Capabilities

### Core Features

1. **Image Management**
   - Upload images (JPG, PNG, WEBP)
   - Automatic thumbnail generation
   - Mobile-optimized versions
   - Image validation (size, dimensions, format)
   - EXIF metadata extraction

2. **Organization**
   - Albums (nested structure)
   - Categories (events, team, office, community, awards)
   - Featured status
   - Display order
   - Active/inactive status

3. **Social Features**
   - Like images (session-based)
   - Share images (multiple platforms)
   - Comment on images
   - Download images (if allowed)
   - Track all interactions

4. **Search & Filter**
   - Full-text search
   - AI tag search
   - Category filtering
   - Album filtering
   - Featured filtering

5. **Analytics**
   - View tracking
   - Like tracking
   - Share tracking
   - Download tracking
   - Engagement metrics
   - Category distribution

6. **AI Features**
   - Auto-tagging
   - Object detection
   - Scene classification
   - Sentiment analysis
   - Color palette detection
   - Quality scoring

7. **Smart Collections**
   - Auto-curated collections
   - Rule-based matching
   - Dynamic updates
   - Manual update option

8. **Auto-Categorization**
   - Rule-based categorization
   - Batch processing
   - Priority-based execution
   - Statistics tracking

### Advanced Features

1. **Responsive Design**
   - Desktop, tablet, mobile support
   - Touch-friendly controls
   - Adaptive images

2. **Performance**
   - Database indexes (20+)
   - Query optimization (93% reduction)
   - Lazy loading
   - Image caching

3. **Security**
   - CSRF protection
   - Authentication checks
   - Input validation
   - File type validation
   - Size limits

4. **Admin Interface**
   - Visual thumbnails
   - Bulk operations
   - Batch upload
   - Drag & drop
   - Date filtering
   - Autocomplete fields

---

## Workflows

### Uploading and Publishing Images

1. **Prepare Images**:
   - Ensure JPG, PNG, or WEBP format
   - Max size: 10MB
   - Dimensions: 100x100 to 5000x5000

2. **Upload to Gallery**:
   - Login to admin panel
   - Go to Gallery → Images
   - Click "Add Image" or "Bulk Upload"
   - Select images
   - Fill in details (title, description, category, album)
   - Click "Save"

3. **Verify**:
   - Check images appear in gallery
   - Verify thumbnails generated
   - Test mobile optimization

### Creating an Album

1. **Plan Structure**:
   - Decide on album name
   - Choose parent album (if nested)
   - Create folder structure

2. **Create Album**:
   - Go to Gallery → Albums
   - Click "Add Album"
   - Enter name and description
   - Upload cover image (optional)
   - Set featured status
   - Click "Save"

3. **Add Images**:
   - Upload images to the album
   - Or move existing images to the album

### Organizing Gallery

1. **By Category**:
   - Assign category to each image
   - Users can filter by category

2. **By Album**:
   - Group related images
   - Create nested album structure
   - Use meaningful names

3. **By Featured Status**:
   - Mark important images as featured
   - Featured images appear on homepage

### Managing Comments

1. **Review Comments**:
   - Go to Gallery → Comments
   - See pending comments

2. **Approve/Reject**:
   - Review comment content
   - Click "Approve" or "Reject"
   - Or edit before approving

3. **Monitor Activity**:
   - View comment analytics
   - Track engagement

---

## Troubleshooting

### Common Issues

#### Images Not Displaying

**Possible Causes**:
1. Image not uploaded properly
2. File path incorrect
3. Permission issues

**Solutions**:
1. Check if file exists in media/gallery/
2. Verify image field is not null
3. Check file permissions
4. Clear browser cache

#### Upload Fails

**Possible Causes**:
1. File too large (over 10MB)
2. Invalid file format
3. Dimensions too large/small
4. Storage full

**Solutions**:
1. Compress images before upload
2. Use JPG, PNG, or WEBP only
3. Resize images to valid dimensions
4. Check disk space

#### Search Not Working

**Possible Causes**:
1. JavaScript error
2. API endpoint issue
3. No results found

**Solutions**:
1. Check browser console for errors
2. Verify API endpoint is accessible
3. Try different search terms

#### Admin Panel Issues

**Possible Causes**:
1. Not logged in
2. Missing permissions
3. Model registration issue

**Solutions**:
1. Login to admin
2. Check user permissions
3. Verify model registration in admin_site.py

### Getting Help

1. Check error logs: `logs/django.log`
2. Review documentation
3. Contact development team
4. Check GitHub issues (if applicable)

---

## Appendix

### Image Specifications

**Supported Formats**: JPG, JPEG, PNG, WEBP

**Size Limits**:
- Maximum file size: 10MB
- Minimum dimensions: 100x100 pixels
- Maximum dimensions: 5000x5000 pixels

**Recommended Settings**:
- Format: JPG (for photos), PNG (for graphics with transparency)
- Quality: 85-90 for JPG
- Resolution: 1920x1080 for display images
- Thumbnails: Auto-generated at 300x200 and 800x600

### Categories

Available categories:
- **events**: Events and gatherings
- **team**: Team activities
- **office**: Office life
- **community**: Community work
- **awards**: Awards and recognition

### Keyboard Shortcuts

**Gallery View**:
- `ESC`: Close lightbox
- `←`: Previous image
- `→`: Next image
- `F`: Focus search box

### Browser Support

**Supported Browsers**:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

### Performance Benchmarks

**Page Load Times**:
- Gallery page: < 200ms
- Album page: < 150ms
- API responses: < 50ms

**Query Performance**:
- Gallery view: 5 queries (was 80+)
- Album API: 1 query (was 20+)
- Search: < 100ms

---

## Quick Reference

### Admin URLs
- `/admin/gallery/galleryalbum/` - Manage albums
- `/admin/gallery/galleryimage/` - Manage images
- `/admin/gallery/galleryimagelike/` - View likes
- `/admin/gallery/galleryimagecomment/` - Moderate comments
- `/admin/gallery/galleryimageshare/` - Track shares
- `/admin/gallery/galleryimagedownload/` - Track downloads
- `/admin/gallery/smartcollection/` - Smart collections
- `/admin/gallery/autocategorizationrule/` - Auto-categorization rules

### Public URLs
- `/gallery/` - Main gallery page
- `/gallery/album/{id}/` - Album detail page
- `/gallery/analytics/` - Analytics dashboard
- `/gallery/vr/` - VR gallery view

### API Endpoints
- `/gallery/api/images/` - Get images (paginated)
- `/gallery/api/search/?query=keyword` - Search images
- `/gallery/api/albums/` - Get albums
- `/gallery/api/categories/` - Get categories
- `/gallery/api/analytics/` - Track interactions
- `/gallery/api/stats/` - Get statistics

---

**Last Updated**: Today  
**Version**: 2.0  
**Maintained By**: Development Team

For questions or support, contact the development team.
