"""
Constants for the Downloads app.
"""

# File Upload Constants
MAX_DOWNLOAD_FILE_SIZE_MB = 50
MAX_DOWNLOAD_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

ALLOWED_DOWNLOAD_FILE_EXTENSIONS = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
    '.ppt', '.pptx', '.txt', '.jpg', '.jpeg', '.png'
]

ALLOWED_DOWNLOAD_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}

# Security Constants
DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl', '.sh', '.ps1'
}

SUSPICIOUS_PATTERNS = [
    b'<script', b'javascript:', b'vbscript:', b'onload=', b'onerror=',
    b'eval(', b'exec(', b'system(', b'shell_exec('
]

# Display Constants
FILES_PER_CATEGORY_DEFAULT = 6  # Number of files to show per category initially

# Pagination Constants
DEFAULT_PAGE_SIZE = 20
ADMIN_LIST_PER_PAGE = 25

# Cache Constants
CACHE_TIMEOUT = 300  # 5 minutes
FEATURED_FILES_CACHE_KEY = 'downloads:featured_files'

