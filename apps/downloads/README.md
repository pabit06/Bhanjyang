# Downloads App Documentation
# (डाउनलोड App कागजातहरू)

**Version:** 2.0.1  
**Django Version:** 5.2.9  
**Status:** ✅ Production Ready (Score: 9.2/10)  
**Maintainer:** Prem Bhandari
**Last Updated:** January 21, 2026

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Models](#models)
5. [Views](#views)
6. [Services](#services)
7. [Security](#security)
8. [Performance](#performance)
9. [Templates](#templates)
10. [Management Commands](#management-commands)
11. [Tests](#tests)
12. [Configuration](#configuration)
13. [API](#api)
14. [Usage Examples](#usage-examples)
15. [Contributing](#contributing)

---

## 🎯 Overview

The Downloads app provides a comprehensive file management system for the Bhanjyang Cooperative website. It enables administrators to upload, organize, and share downloadable files with members and visitors while tracking usage analytics and maintaining security.

**Key Capabilities:**
- Secure file upload and storage
- Categorical organization (8 predefined categories)
- Access control (public/login-required)
- Download analytics and tracking
- Bulk download support
- File expiration management
- Virus scanning and validation
- CDN integration for performance

---

## ✨ Features

### 📁 File Management
- **Upload Files**: Support for PDF, Office documents, images
- **Categorization**: 8 categories (Forms, Reports, Policies, Publications, Manuals, Certificates, Brochures, Other)
- **Priority Levels**: Low, Medium, High, Urgent
- **Featured Files**: Highlight important documents
- **Tags**: Flexible tagging system for organization
- **Thumbnails**: Optional preview images

### 🔐 Security & Access Control
- **File Validation**: Extension and MIME type checking
- **Virus Scanning**: Automatic ClamAV integration
- **Access Control**: Login-required downloads
- **File Expiration**: Automatic expiry dates
- **Security Hash**: SHA-256 file integrity ✅ **Enhanced with download verification**
- **File Integrity Check**: ✅ Hash verification on download to detect tampering
- **Secure File Serving**: ✅ Files served through Django views (no direct URL access)
- **Media Storage Security**: ✅ Server-level blocking of direct media access
- **Audit Logging**: Complete download history
- **Rate Limiting**: ✅ Enhanced with per-user and per-IP rate limiting
- **IP Blacklist**: ✅ Block malicious IPs with comprehensive logging
- **Content Security Policy (CSP)**: ✅ CSP headers for XSS protection
- **Security Headers**: ✅ X-Content-Type-Options, X-Frame-Options, etc.
- **Structured Error Codes**: ✅ Consistent error handling and better debugging

### 📊 Analytics & Tracking
- **Download Count**: Track file popularity
- **View Count**: Monitor file views
- **Access Tracking**: Last accessed timestamp
- **Statistics Dashboard**: Aggregate analytics
- **Category Analytics**: Per-category metrics

### 🚀 Performance
- **Query Optimization**: Efficient database queries
- **Caching**: Redis-based caching layer
- **CDN Support**: CloudFlare/AWS CloudFront
- **Lazy Loading**: Optimized page loads
- **Performance Monitoring**: ✅ Full integration with PerformanceMetric model
  - Service-level performance tracking
  - Database query monitoring
  - Download operation performance tracking
  - Bulk download performance tracking
  - Cache performance monitoring
  - Slow operation detection (>500ms threshold)

### 📦 Bulk Operations
- **Bulk Download**: Download multiple files as ZIP
- **Bulk Upload**: Admin batch upload (planned)
- **Bulk Update**: Mass update operations

---

## 💿 Installation

### Prerequisites
- Python 3.10+
- Django 5.2+
- PostgreSQL 13+ (recommended)
- Redis 6+ (for caching)
- ClamAV (for virus scanning)

### Setup Steps

1. **Install ClamAV** (for virus scanning):
```bash
# Ubuntu/Debian
sudo apt-get install clamav clamav-daemon

# macOS
brew install clamav

# Windows
# Download from: https://www.clamav.net/downloads
```

2. **Configure Settings** (`config/settings.py`):
```python
INSTALLED_APPS = [
    # ...
    'apps.downloads',
]

# Downloads App Settings
DOWNLOADS_SETTINGS = {
    'ENABLE_VIRUS_SCAN': True,
    'MAX_FILE_SIZE': 50 * 1024 * 1024,  # 50MB
    'ALLOWED_EXTENSIONS': [
        'pdf', 'doc', 'docx', 'xls', 'xlsx',
        'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'
    ],
    'ENABLE_CDN': True,
    'CDN_BASE_URL': 'https://cdn.bhanjyang.coop',
}
```

3. **Run Migrations**:
```bash
python manage.py migrate downloads
```

4. **Collect Static Files**:
```bash
python manage.py collectstatic
```

5. **Create Superuser** (if needed):
```bash
python manage.py createsuperuser
```

---

## 📊 Models

### DownloadableFile

Main model for managing downloadable files.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `category` | CharField | File category (FK to FileCategory) |
| `title` | CharField(200) | File title |
| `description` | TextField | File description |
| `file` | FileField | Uploaded file |
| `is_active` | BooleanField | Visibility flag |
| `is_featured` | BooleanField | Featured status |
| `priority` | CharField | Priority level (FK to PriorityLevel) |
| `requires_login` | BooleanField | Login requirement |
| `expires_at` | DateTimeField | Expiration date (optional) |
| `tags` | CharField(500) | Comma-separated tags |
| `thumbnail` | ImageField | Preview image (optional) |
| `download_count` | PositiveIntegerField | Download counter |
| `view_count` | PositiveIntegerField | View counter |
| `uploaded_at` | DateTimeField | Upload timestamp |
| `updated_at` | DateTimeField | Last update |
| `file_hash` | CharField(64) | SHA-256 hash |
| `uploaded_by` | ForeignKey(User) | Uploader |
| `last_accessed` | DateTimeField | Last access time |
| `access_count` | PositiveIntegerField | Total accesses |
| `file_type` | CharField(10) | File extension |

**Methods:**

```python
def increment_view_count(self)
    """Atomically increment view counter."""

def increment_download_count(self)
    """Atomically increment download counter."""

@property
def file_size(self) -> str
    """Returns human-readable file size (e.g., '2.5 MB')."""

@property
def is_expired(self) -> bool
    """Check if file has expired."""

@property
def tag_list(self) -> list
    """Returns tags as a list."""
```

**Example:**
```python
from apps.downloads.models import DownloadableFile, FileCategory

# Create a new file
file = DownloadableFile.objects.create(
    category=FileCategory.FORM,
    title='Membership Application Form',
    description='New member registration form',
    file=uploaded_file,
    priority=PriorityLevel.HIGH,
    is_featured=True,
    tags='membership, application, form',
    requires_login=False
)

# Check file size
print(file.file_size)  # Output: "1.2 MB"

# Increment download count
file.increment_download_count()
```

---

## 🎨 Views

### Function-Based Views

The app uses function-based views with service layer separation for business logic.

#### download_center_view

**URL:** `/downloads/`  
**Purpose:** Main download center page  
**Features:**
- Category filtering
- Priority filtering
- Search functionality
- Pagination
- "Show More" functionality

**Parameters:**
- `category` (optional): Filter by category code
- `priority` (optional): Filter by priority
- `featured` (optional): Show only featured files
- `q` (optional): Search query
- `show_all` (optional): Show all files vs. limited

**Example:**
```python
# URLs
/downloads/                          # All files
/downloads/?category=FRM            # Forms only
/downloads/?priority=HIGH           # High priority
/downloads/?featured=true           # Featured files
/downloads/?q=membership            # Search
```

#### download_file_view

**URL:** `/downloads/<pk>/download/`  
**Purpose:** Handle file downloads  
**Features:**
- Login check (if required)
- Expiration check
- Download counter increment
- Audit logging
- Redirect to file URL

#### file_detail_view

**URL:** `/downloads/<pk>/`  
**Purpose:** File detail page  
**Features:**
- View counter increment
- Related files
- File metadata display

#### bulk_download_view

**URL:** `/downloads/bulk-download/`  
**Method:** POST  
**Purpose:** Download multiple files as ZIP  
**Features:**
- Access control
- ZIP creation
- Progress tracking

---

## 🔧 Services

Service layer handles business logic separate from views.

### DownloadsService

Handles download center operations.

**Methods:**

```python
class DownloadsService:
    @staticmethod
    def get_download_center_context(request_params, show_all=False):
        """
        Get context data for the download center page.
        
        Args:
            request_params: Dictionary with query parameters
            show_all: Boolean indicating whether to show all files
            
        Returns:
            dict: Context dictionary for the template
        """
        
    @staticmethod
    def _get_filtered_files(category_code, priority_code, 
                           featured_only, query):
        """
        Get filtered list of downloadable files.
        
        Returns:
            QuerySet: Filtered DownloadableFile queryset
        """
        
    @staticmethod
    def _group_files_by_category(downloads_list, show_all=False):
        """
        Group files by category with "Show More" functionality.
        
        Returns:
            dict: Dictionary with category codes as keys
        """
```

**Example:**
```python
from apps.downloads.services import DownloadsService

# Get context for download center
context = DownloadsService.get_download_center_context(
    request_params={
        'category': 'FRM',
        'priority': 'HIGH',
        'q': 'application'
    },
    show_all=False
)
```

### FileDownloadService

Manages file download operations.

**Methods:**

```python
class FileDownloadService:
    @staticmethod
    def process_file_download(request, file_obj):
        """
        Process a file download request.
        
        Args:
            request: HTTP request object
            file_obj: DownloadableFile instance
            
        Returns:
            tuple: (success: bool, response_or_redirect, error_message: str)
        """
        
    @staticmethod
    def process_file_view(request, file_obj):
        """
        Process a file view request (increment view count).
        
        Returns:
            bool: Success status
        """
```

### BulkDownloadService

Handles bulk download operations.

**Methods:**

```python
class BulkDownloadService:
    @staticmethod
    def get_accessible_files(user, file_ids):
        """
        Get list of files that user can download.
        
        Returns:
            list: List of DownloadableFile objects user can access
        """
        
    @staticmethod
    def create_zip_file(file_objects):
        """
        Create a ZIP file containing multiple files.
        
        Returns:
            tuple: (temp_file_path: str, success_count: int, 
                   failed_files: list)
        """
```

### DownloadsAnalyticsService

Provides download statistics.

**Methods:**

```python
class DownloadsAnalyticsService:
    @staticmethod
    def get_download_stats():
        """
        Get statistics about downloads.
        
        Returns:
            dict: Dictionary with various statistics
        """
```

**Example:**
```python
from apps.downloads.services import DownloadsAnalyticsService

stats = DownloadsAnalyticsService.get_download_stats()
print(f"Total downloads: {stats['total_downloads']}")
print(f"Total files: {stats['total_files']}")
print(f"Most popular: {stats['most_downloaded']['title']}")
```

---

## 🔒 Security

### File Validation

**FileSecurityValidator**

Validates uploaded files for security.

**Checks:**
- File extension whitelist
- File size limits
- MIME type verification  
- Content inspection
- Malicious content detection

**Example:**
```python
from apps.downloads.security import FileSecurityValidator

validation_result = FileSecurityValidator.validate_file_security(
    uploaded_file
)

if validation_result['is_valid']:
    # Proceed with upload
    file_hash = validation_result['file_hash']
else:
    # Reject upload
    errors = validation_result['errors']
```

### Virus Scanning ✅ **ENHANCED**

**VirusScanManager**

Integrates with ClamAV for virus scanning on both upload and download.

**Features:**
- ✅ **Automatic scanning on download** - Files scanned before serving
- ✅ **Automatic scanning on upload** - Files scanned during upload (optional)
- ✅ **ClamAV integration** - Uses pyclamd library for ClamAV daemon communication
- ✅ **Unix socket and TCP support** - Automatic fallback to TCP if socket unavailable
- ✅ **Configurable timeout** - Customizable scan timeout per file
- ✅ **Scan result logging** - All scan results logged for audit
- ✅ **Error handling** - Graceful handling when ClamAV unavailable

**Implementation:**
```python
from apps.downloads.security import VirusScanManager

# Scan file before download
is_clean, scan_result = VirusScanManager.scan_file(file_path)

if not is_clean:
    # Virus detected - block download
    return False, None, DownloadsErrorCodes.VIRUS_DETECTED
```

**Configuration:**
```python
DOWNLOADS_SETTINGS = {
    'ENABLE_VIRUS_SCAN': True,  # Enable virus scanning
    'VIRUS_SCAN_TIMEOUT': 30,   # Timeout in seconds
    'REQUIRE_VIRUS_SCAN': False,  # Block if scan fails (default: False)
    'CLAMAV_HOST': '127.0.0.1',   # ClamAV TCP host (optional)
    'CLAMAV_PORT': 3310,         # ClamAV TCP port (optional)
}
```

**Scan Timing:**
1. **On Download**: Files are scanned before being served to users
2. **On Upload**: Files can be scanned during upload (optional, via model save)

**Error Codes:**
- `VIRUS_DETECTED`: Returned when virus is detected (403 Forbidden)

**Dependencies:**
- ClamAV daemon must be installed and running
- `pyclamd` Python library (install with: `pip install pyclamd`)

### Access Control

**AccessControlManager**

Manages file access permissions.

**Checks:**
- User authentication (if required)
- File expiration
- IP-based restrictions ✅ Implemented
- Rate limiting ✅ Enhanced with per-user and per-IP

### Rate Limiting (NEW in v2.0.0)

**Enhanced Rate Limiting System**

Multi-layer rate limiting for download protection.

**Features:**
- Per-user rate limiting (for authenticated users)
- Per-IP rate limiting (for all users)
- Middleware-based implementation
- Configurable limits per action type
- Proper 429 responses with error codes
- User-friendly error messages

**Rate Limits:**
- Download operations: Configurable per user/IP
- Bulk downloads: Separate limits
- Automatic reset after time window

**Error Handling:**
- Structured error codes (`DownloadsErrorCodes.RATE_LIMIT_EXCEEDED`)
- User-friendly messages
- Proper HTTP status codes (429)

### Security Headers (NEW in v2.0.0)

**Content Security Policy (CSP)**

CSP headers for enhanced XSS protection.

**Headers Added:**
- `Content-Security-Policy`: Restricts resource loading
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block
- `Referrer-Policy`: strict-origin-when-cross-origin
- `Permissions-Policy`: Restrictive permissions

**CSP Policy:**
- Allows necessary external resources (CDN, fonts)
- Blocks inline scripts (except where necessary)
- Prevents XSS attacks
- Restricts frame embedding

### File Integrity Check (NEW in v2.0.0)

**Hash Verification on Download**

SHA-256 hash verification ensures files haven't been tampered with.

**How It Works:**
1. **On Upload**: SHA-256 hash is calculated and stored in database
2. **On Download**: Hash is recalculated and compared with stored hash
3. **If Mismatch**: Download is blocked with `FILE_INTEGRITY_FAILED` error

**Implementation:**
```python
from apps.downloads.security import FileSecurityValidator

# Verify file integrity
is_valid, current_hash, error_msg = FileSecurityValidator.verify_file_hash(
    file_path='/path/to/file.pdf',
    expected_hash='stored_hash_from_database'
)

if not is_valid:
    # File has been tampered with
    logger.error(f"File integrity check failed: {error_msg}")
```

**Error Handling:**
- Returns `DownloadsErrorCodes.FILE_INTEGRITY_FAILED` if hash mismatch
- Logs security event for admin review
- Blocks download to prevent serving compromised files

**Benefits:**
- Detects file tampering
- Ensures file authenticity
- Protects against unauthorized modifications
- Maintains audit trail

### Secure File Serving (NEW in v2.0.0)

**Media Storage Security**

Files are served securely through Django views, preventing direct URL access.

**How It Works:**
1. Files stored in `media/downloads/` are blocked from direct access
2. All downloads go through `/downloads/<pk>/download/` endpoint
3. Access control, expiration, and integrity checks are enforced
4. Files are served via `/downloads/<pk>/serve/` secure view
5. Server configuration (`.htaccess`/Nginx) blocks direct media URLs

**Implementation:**
```python
# Secure file serving view
class SecureFileServeView(View):
    def get(self, request, pk):
        # Verify permissions
        # Check expiration
        # Validate integrity
        # Serve file with proper headers
```

**Server Configuration:**
- **Apache**: `.htaccess` in `media/downloads/` blocks direct access
- **Nginx**: Location block denies `/media/downloads/` direct access
- See `docs/deployment/media-security.md` for details

**Benefits:**
- ✅ Prevents direct URL access to files
- ✅ Enforces access control on every download
- ✅ Ensures download tracking and logging
- ✅ Maintains file integrity verification
- ✅ Protects against unauthorized file sharing

### Audit Logging

**SecurityAuditLogger**

Logs all security-related events.

**Events Logged:**
- File downloads
- Failed access attempts
- Security violations
- Virus detections
- Rate limit violations
- IP blacklist blocks
- **File integrity check failures** ✅ NEW
- **Secure file serving access** ✅ NEW

### Error Handling (NEW in v2.0.0)

**Structured Error Codes**

Consistent error handling with structured error codes.

**Error Code System:**
```python
from apps.downloads.utils.error_codes import (
    DownloadsErrorCodes,
    get_status_code_for_error,
    get_user_friendly_message
)

# Use error codes in responses
error_code = DownloadsErrorCodes.FILE_EXPIRED
status_code = get_status_code_for_error(error_code)  # 410
message = get_user_friendly_message(error_code)     # User-friendly message
```

**Available Error Codes:**
- `DOWNLOAD_ERROR`: General download errors
- `FILE_NOT_FOUND`: File not found (404)
- `ACCESS_DENIED`: Access denied (403)
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded (429)
- `FILE_EXPIRED`: File expired (410)
- `INVALID_FILE_TYPE`: Invalid file type (400)
- `BULK_DOWNLOAD_ERROR`: Bulk download errors (500)
- `VIRUS_DETECTED`: Virus detected (403)
- `IP_BLACKLISTED`: IP blacklisted (403)
- And more...

**Benefits:**
- Consistent error responses
- Better debugging and logging
- User-friendly error messages
- Proper HTTP status codes

---

## ⚡ Performance

### Caching

**DownloadsCache**

Redis-based caching for improved performance.

**Cached Data:**
- Download center context
- File listings
- Category groupings
- Statistics

**Cache Keys:**
```python
downloads_center_all
downloads_center_category_{code}
downloads_featured
downloads_stats
```

### Query Optimization

**DownloadsQueryOptimizer**

Optimizes database queries.

**Optimizations:**
- `select_related()` for ForeignKeys
- `prefetch_related()` for Many-to-Many
- Indexed fields for filtering
- Efficient counting queries

### CDN Support ✅ **ENHANCED**

**CDNManager**

Integrates with CDN for file delivery with automatic URL generation.

**Supported CDNs:**
- ✅ CloudFlare
- ✅ AWS CloudFront
- ✅ Custom CDN

**Features:**
- ✅ Automatic CDN URL generation for public files
- ✅ Configurable minimum download threshold
- ✅ Secure files always go through Django views
- ✅ Easy integration with existing code

**Usage:**
```python
from apps.downloads.utils.cdn import CDNManager

# Get CDN URL for file
cdn_url = CDNManager.get_cdn_url(file_url, file_obj)

# Get secure download URL (with CDN if applicable)
download_url = CDNManager.get_secure_download_url(file_obj, request)
```

### Performance Monitoring (NEW in v2.0.0)

**Performance Tracking System**

Comprehensive performance monitoring integrated with `PerformanceMetric` model.

**Features:**
- Service-level performance tracking with decorators
- Database query monitoring (query count, slow queries)
- Download operation performance tracking
- Bulk download performance tracking
- Cache performance monitoring (hits/misses, lookup times)
- Slow operation detection (>500ms threshold)
- Automatic alerting for performance issues

**Usage:**
```python
from apps.downloads.utils.performance import track_performance, track_download_performance

# Decorator for service methods
@track_performance('download_center', '/downloads/')
def get_download_center_context(request_params, show_all=False):
    # Service method implementation
    pass

# Track download performance
track_download_performance(
    download_time=150.5,  # milliseconds
    file_size=1024000,    # bytes
    request_meta=request.META,
    user=request.user,
    session_id=request.session.session_key,
    file_id=file_obj.pk
)
```

**Performance Metrics Tracked:**
- `download_center`: Download center page load time
- `file_download`: Individual file download time
- `bulk_download`: Bulk download operation time
- `cache_operation`: Cache hit/miss performance
- `api_response`: API endpoint response times

### Performance Optimizations (NEW in v2.0.0)

**Chunked Downloads** ✅

Large files (50MB+) are served using `StreamingHttpResponse` to prevent loading entire file into memory.

**Benefits:**
- ✅ Reduces server RAM usage
- ✅ Faster response time for large files
- ✅ Better scalability
- ✅ Automatic fallback to regular response for small files

**Implementation:**
```python
# In SecureFileServeView
if file_size >= 50 * 1024 * 1024:  # 50MB
    response = StreamingHttpResponse(
        file_iterator(file_path),
        content_type=content_type
    )
else:
    # Regular HttpResponse for smaller files
    response = HttpResponse(file_content, content_type=content_type)
```

**Asynchronous Bulk Downloads** ✅

Large bulk downloads (10+ files) are processed asynchronously using Celery.

**Features:**
- ✅ Background ZIP creation for large bulk downloads
- ✅ Email notification when ZIP is ready
- ✅ Task status polling endpoint
- ✅ Automatic cleanup of old bulk download files
- ✅ Fallback to synchronous processing if Celery unavailable

**Implementation:**
```python
# In BulkDownloadView
if use_async and len(files) >= async_threshold:
    task = create_bulk_download_zip_task.delay(
        file_ids=[f.id for f in files],
        user_id=request.user.id,
        notification_email=user.email
    )
    return JsonResponse({'status': 'processing', 'task_id': task.id})
```

**Task Status Check:**
```python
# GET /downloads/bulk-download/status/<task_id>/
# Returns: {'status': 'success|processing|error', 'download_url': '...'}
```

**CDN Support** ✅

CDN integration for frequently downloaded public files.

**Features:**
- ✅ Configurable CDN provider (CloudFront, Cloudflare, custom)
- ✅ Automatic CDN URL generation for public files
- ✅ Minimum download threshold before using CDN
- ✅ Secure files always go through Django views

**Configuration:**
```python
DOWNLOADS_SETTINGS = {
    'ENABLE_CDN': True,
    'CDN_BASE_URL': 'https://cdn.example.com',
    'CDN_PROVIDER': 'cloudfront',  # or 'cloudflare'
    'CDN_MIN_DOWNLOADS': 10,  # Use CDN after 10 downloads
}
```

**Usage:**
```python
from apps.downloads.utils.cdn import CDNManager

# Get CDN URL for file
cdn_url = CDNManager.get_cdn_url(file_url, file_obj)

# Get secure download URL (with CDN if applicable)
download_url = CDNManager.get_secure_download_url(file_obj, request)
```

---

## 🎨 Templates

### download.html

Main download center template.

**Sections:**
- Hero section
- Category filters
- Search bar
- Featured files
- Files grouped by category
- Pagination

**JavaScript Features:**
- AJAX filtering
- "Show More" functionality
- Bulk selection
- Download tracking

---

## 🛠️ Management Commands

### cleanup_expired_files

Removes expired files from storage.

**Usage:**
```bash
python manage.py cleanup_expired_files
```

**Options:**
- `--dry-run`: Show what would be deleted
- `--days`: Delete files expired for N days

### generate_download_stats

Generates download statistics.

**Usage:**
```bash
python manage.py generate_download_stats
```

---

## 🧪 Tests

### Test Coverage: ~86% ✅ (Target Met)

**Test Files:**
```
tests/
├── test_models.py          # Model tests
├── test_views.py           # View tests
├── test_services.py        # Service tests
├── test_services_comprehensive.py  # Comprehensive service tests
├── test_security.py        # Security tests
├── test_security_enhanced.py  # Enhanced security tests
├── test_performance.py     # Performance tests
├── test_view_errors.py     # View error handling tests
├── test_context_processors.py  # Context processor tests
├── test_refactor_verification.py  # Refactor verification tests
├── test_file_integrity.py  # File integrity check tests
└── test_virus_scanning.py  # Virus scanning tests
```

**Run Tests:**
```bash
# All tests
python manage.py test apps.downloads

# Specific test file
python manage.py test apps.downloads.tests.test_models

# With coverage
coverage run --source='apps/downloads' manage.py test apps.downloads
coverage report

# With HTML report
coverage html
```

**Test Coverage Goals:**
- Target: 85%+ coverage
- Focus areas: Error codes, helpers, enhanced middleware, performance tracking

---

## ⚙️ Configuration

### Settings

Add to `config/settings.py`:

```python
# Downloads App Configuration
DOWNLOADS_SETTINGS = {
    # File Upload
    'MAX_FILE_SIZE': 50 * 1024 * 1024,  # 50MB
    'ALLOWED_EXTENSIONS': [
        'pdf', 'doc', 'docx', 'xls', 'xlsx',
        'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png'
    ],
    
    # Security
    'ENABLE_VIRUS_SCAN': True,
    'VIRUS_SCAN_TIMEOUT': 30,  # seconds
    'ENABLE_FILE_HASH': True,
    
    # Performance
    'ENABLE_CACHING': True,
    'CACHE_TIMEOUT': 3600,  # 1 hour
    'ENABLE_CDN': False,
    'CDN_BASE_URL': '',
    
    # Features
    'FILES_PER_CATEGORY': 6,  # Show More functionality
    'ENABLE_BULK_DOWNLOAD': True,
    'BULK_DOWNLOAD_LIMIT': 20,  # max files
    
    # Rate Limiting ✅ Implemented
    'ENABLE_RATE_LIMIT': True,
    'MAX_DOWNLOADS_PER_HOUR': 20,
    'MAX_DOWNLOADS_PER_USER_PER_HOUR': 15,
    
    # Performance Optimizations ✅ NEW
    'ENABLE_ASYNC_BULK_DOWNLOAD': True,  # Use Celery for large bulk downloads
    'ASYNC_BULK_DOWNLOAD_THRESHOLD': 10,  # Files count threshold for async
    'ENABLE_CDN': False,  # Enable CDN for public files
    'CDN_BASE_URL': '',  # CDN base URL (e.g., 'https://cdn.example.com')
    'CDN_PROVIDER': None,  # 'cloudfront', 'cloudflare', or None
    'CDN_MIN_DOWNLOADS': 10,  # Minimum downloads before using CDN
}
```

---

## 🌐 API

**Status:** ✅ Fully Implemented  
**Implementation:** Complete REST API using Django REST Framework

### Available Endpoints:

The API provides comprehensive RESTful endpoints for file management:

**CRUD Operations:**
```
GET    /api/downloads/files/                      # List all files
POST   /api/downloads/files/                      # Create file (admin only)
GET    /api/downloads/files/{id}/                 # Get file details
PUT    /api/downloads/files/{id}/                 # Update file (admin only)
PATCH  /api/downloads/files/{id}/                 # Partial update (admin only)
DELETE /api/downloads/files/{id}/                 # Delete file (admin only)
```

**Custom Actions:**
```
POST   /api/downloads/files/{id}/download/        # Download file
POST   /api/downloads/files/{id}/increment_view/  # Increment view count
GET    /api/downloads/files/featured/             # Get featured files
GET    /api/downloads/files/categories/           # Get categories list
GET    /api/downloads/files/priorities/           # Get priorities list
GET    /api/downloads/files/stats/                # Get statistics (admin only)
```

### API Features:

**Filtering & Search:**
- Filter by category, priority, featured status, login requirement
- Date range filtering (uploaded_at)
- Full-text search on title, description, and tags
- Ordering by uploaded_at, download_count, view_count, priority, title

**Authentication & Permissions:**
- Read operations: Public access (IsAuthenticatedOrReadOnly)
- Write operations: Admin only (IsAdminUser)
- Statistics endpoint: Admin only

**Security:**
- Integrated with SecurityAuditEnhancedLogger
- Request validation
- Proper error handling with structured error codes
- Performance tracking with `track_api_response_time`

**Serializers:**
- `DownloadableFileSerializer` - Full file details
- `DownloadableFileListSerializer` - Optimized for list views
- `DownloadableFileCreateUpdateSerializer` - For create/update operations
- `FileCategorySerializer` - Category information
- `FilePrioritySerializer` - Priority information
- `FileStatsSerializer` - Statistics data

### Usage Example:

```python
import requests

# List files with filtering
response = requests.get('http://example.com/api/downloads/files/', params={
    'category': 'FRM',
    'priority': 'HIGH',
    'search': 'application',
    'ordering': '-uploaded_at'
})

# Get file details
response = requests.get('http://example.com/api/downloads/files/1/')

# Download file (requires authentication)
response = requests.post(
    'http://example.com/api/downloads/files/1/download/',
    headers={'Authorization': 'Token your-token-here'}
)

# Get featured files
response = requests.get('http://example.com/api/downloads/files/featured/')
```

### API Configuration:

The API is configured in `apps/downloads/api_urls.py` and uses Django REST Framework's DefaultRouter. Make sure to include the API URLs in your main URL configuration:

```python
# In your main urls.py
urlpatterns = [
    # ...
    path('api/downloads/', include('apps.downloads.api_urls')),
]
```

---

## 📚 Usage Examples

### Upload a File (Admin)

```python
from apps.downloads.models import DownloadableFile, FileCategory

file = DownloadableFile.objects.create(
    category=FileCategory.FORM,
    title='Annual Report 2024',
    description='Financial and operational report for 2024',
    file=request.FILES['file'],
    priority=PriorityLevel.HIGH,
    is_featured=True,
    requires_login=False
)
```

### Filter Files

```python
# Get all active forms
forms = DownloadableFile.objects.filter(
    category=FileCategory.FORM,
    is_active=True
)

# Get featured high-priority files
featured = DownloadableFile.objects.filter(
    is_featured=True,
    priority=PriorityLevel.HIGH
)

# Search by title
results = DownloadableFile.objects.filter(
    title__icontains='application'
)
```

### Track Downloads

```python
# Increment download count
file.increment_download_count()

# Get popular files
popular = DownloadableFile.objects.filter(
    is_active=True
).order_by('-download_count')[:10]
```

### Use the REST API

```python
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

# Initialize API client
client = APIClient()

# List files (public access)
response = client.get('/api/downloads/files/')
files = response.data['results']  # Paginated results

# Filter files by category
response = client.get('/api/downloads/files/', {'category': 'FRM'})

# Search files
response = client.get('/api/downloads/files/', {'search': 'application'})

# Get file details
response = client.get('/api/downloads/files/1/')
file_data = response.data

# Download file (authenticated)
user = User.objects.get(username='testuser')
client.force_authenticate(user=user)
response = client.post('/api/downloads/files/1/download/')

# Get featured files
response = client.get('/api/downloads/files/featured/')

# Get statistics (admin only)
admin_user = User.objects.get(is_staff=True)
client.force_authenticate(user=admin_user)
response = client.get('/api/downloads/files/stats/')
stats = response.data
```

---

## 🤝 Contributing

### Development Setup

1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Run migrations
5. Create test data

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

### Pull Request Process

1. Create feature branch
2. Write tests
3. Update documentation
4. Submit PR with description

---

## 📄 License

Proprietary - Bhanjyang Saving & Credit Cooperative Society Ltd.

---

## 📞 Support

**Issues:** Create GitHub issue  
**Email:** tech@bhanjyang.coop  
**Phone:** +977-9856083101

---

---

## 📊 Version History

### v2.0.1 (January 21, 2026)
**Maintenance Release:**
- ✅ **Test Coverage Increase:** Achieved >85% coverage for core modules (models, utils, security)
- ✅ **Regression Fixes:** Fixed all regression failures in views and context processors
- ✅ **Stability:** Resolved flaky rate-limiting tests
- ✅ **Documentation:** Updated API docs and test guides
- ✅ **API Documentation:** Complete API endpoint documentation added

### v2.0.0 (January 20, 2026)
**Major Enhancements:**
- ✅ Comprehensive performance monitoring system
- ✅ Enhanced rate limiting (per-user + IP-based)
- ✅ Content Security Policy (CSP) headers
- ✅ Structured error codes and consistent error handling
- ✅ Full type hints throughout codebase
- ✅ Enhanced security middleware
- ✅ Improved error handling and debugging
- ✅ **File integrity verification on download** - SHA-256 hash verification
- ✅ **Secure file serving** - Server-level blocking of direct media access
- ✅ **Virus scanning on download** - ClamAV integration for file scanning before serving
- ✅ **Chunked downloads** - StreamingHttpResponse for large files (50MB+)
- ✅ **Asynchronous bulk downloads** - Celery tasks for large ZIP creation
- ✅ **CDN support** - CloudFront/Cloudflare integration for public files
- ✅ Comprehensive RATING.md assessment document

### v1.0.0 (January 6, 2026)
- Initial production release
- Basic file management
- Security features
- Performance optimizations

---

**Last Updated:** January 21, 2026  
**Version:** 2.0.1  
**Status:** ✅ Production Ready (Score: 9.2/10)  
**Next Steps:** Enhance accessibility to WCAG 2.1 Level AA (Priority 2)
