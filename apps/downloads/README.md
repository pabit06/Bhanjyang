# Downloads App Documentation
# (डाउनलोड App कागजातहरू)

**Version:** 1.0.0  
**Django Version:** 5.2.9  
**Status:** Production Ready  
**Maintainer:** Bhanjyang Cooperative Development Team

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
- **Security Hash**: SHA-256 file integrity
- **Audit Logging**: Complete download history
- **Rate Limiting**: Prevent abuse (TODO: Priority 2)
- **IP Blacklist**: Block malicious IPs (TODO: Priority 2)

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

### Virus Scanning

**VirusScanManager**

Integrates with ClamAV for virus scanning.

**Features:**
- Automatic scanning on upload
- Quarantine for infected files
- Scan result logging

### Access Control

**AccessControlManager**

Manages file access permissions.

**Checks:**
- User authentication (if required)
- File expiration
- IP-based restrictions (TODO)
- Rate limiting (TODO)

### Audit Logging

**SecurityAuditLogger**

Logs all security-related events.

**Events Logged:**
- File downloads
- Failed access attempts
- Security violations
- Virus detections

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

### CDN Support

**DownloadsCDNManager**

Integrates with CDN for file delivery.

**Supported CDNs:**
- CloudFlare
- AWS CloudFront
- Custom CDN

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

### Test Coverage: ~60%

**Test Files:**
```
tests/
├── test_models.py          # Model tests
├── test_views.py           # View tests
├── test_services.py        # Service tests
├── test_security.py        # Security tests
├── test_performance.py     # Performance tests
└── test_utils.py           # Utility tests
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
```

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
    
    # Rate Limiting (TODO: Priority 2)
    'ENABLE_RATE_LIMIT': False,
    'MAX_DOWNLOADS_PER_HOUR': 20,
}
```

---

## 🌐 API

**Status:** Not Implemented  
**Planned:** Priority 3 (5-7 days)

### Planned Endpoints:

```
GET    /api/downloads/files/              # List files
GET    /api/downloads/files/{id}/         # File detail
POST   /api/downloads/files/{id}/download/ # Download file
GET    /api/downloads/stats/               # Statistics
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

**Last Updated:** January 6, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready (Score: 78/100)  
**Next Steps:** Implement Priority 2 (Security Enhancements)
