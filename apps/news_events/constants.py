"""
Constants for News Events App.

This module contains all configuration constants to avoid magic numbers
and improve maintainability.
"""

# Pagination Constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Content Limits
DEFAULT_ARTICLE_LIMIT = 6
DEFAULT_EVENT_LIMIT = 3
DEFAULT_FEATURED_LIMIT = 3
DEFAULT_RECENT_LIMIT = 10
DEFAULT_RELATED_LIMIT = 3

# Cache Timeouts (in seconds)
CACHE_TIMEOUT_ARTICLE_LIST = 300  # 5 minutes
CACHE_TIMEOUT_EVENT_LIST = 300  # 5 minutes
CACHE_TIMEOUT_CATEGORY_STATS = 600  # 10 minutes
CACHE_TIMEOUT_ARTICLE_STATS = 900  # 15 minutes
CACHE_TIMEOUT_EVENT_STATS = 900  # 15 minutes
CACHE_TIMEOUT_POPULAR_CONTENT = 1800  # 30 minutes
CACHE_TIMEOUT_ANALYTICS = 3600  # 1 hour
CACHE_TIMEOUT_INVALID_SLUG = 3600  # 1 hour

# Time Ranges for Analytics
ANALYTICS_DEFAULT_DAYS = 30
ANALYTICS_LAST_24_HOURS = 24
ANALYTICS_LAST_7_DAYS = 7

# Reading Time Calculation
AVERAGE_WORDS_PER_MINUTE = 200
MIN_READ_TIME_MINUTES = 1

# Slug Generation
MAX_SLUG_COUNTER = 1000
SLUG_HASH_LENGTH = 12
SLUG_FALLBACK_HASH_LENGTH = 8

# Content Limits
MAX_CONTENT_LENGTH = 100000  # 100KB
MAX_COMMENT_LENGTH = 2000
MAX_TITLE_LENGTH = 200
MAX_EXCERPT_LENGTH = 500
MAX_META_DESCRIPTION_LENGTH = 300
MAX_META_KEYWORDS_LENGTH = 500
MAX_IMAGE_ALT_LENGTH = 200

# Spam Detection
MAX_SPAM_KEYWORDS = 3

# Percentage Calculation
PERCENTAGE_DECIMAL_PLACES = 2

# HTTP Status Codes (for reference)
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500

# Security Constants
SPAM_KEYWORDS = [
    'viagra', 'casino', 'lottery', 'winner', 'congratulations', 'free money',
    'click here', 'limited time', 'act now', 'guaranteed', 'no risk',
    'buy now', 'cheap', 'discount', 'prize', 'urgent'
]

SUSPICIOUS_PATTERNS = [
    r'https?://[^\s]+',  # URLs
    r'\b\d{4}[-.]?\d{4}[-.]?\d{4}[-.]?\d{4}\b',  # Credit card numbers
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
]

DISPOSABLE_EMAIL_DOMAINS = [
    '10minutemail.com', 'tempmail.com', 'guerrillamail.com',
    'mailinator.com', 'yopmail.com', 'temp-mail.org',
    'trashmail.com', 'sharklasers.com', 'guerrillamailblock.com'
]

SUSPICIOUS_EMAIL_DOMAINS = [
    'tempmail.com', '10minutemail.com', 'guerrillamail.com',
    'throwawaymail.com'
]

# Rate Limits
RATE_LIMIT_SUBSCRIPTION_ATTEMPTS = 3
RATE_LIMIT_SUBSCRIPTION_PERIOD = 3600  # 1 hour
RATE_LIMIT_COMMENT_ATTEMPTS = 5
RATE_LIMIT_COMMENT_PERIOD = 3600  # 1 hour

SPAM_SCORE_THRESHOLD = 10
SPAM_LINK_LIMIT = 2
SPAM_REPETITION_THRESHOLD = 0.3  # 30%

