"""
Constants for the Home app.
"""

# Cache Timeouts (in seconds)
CACHE_TIMEOUT_HOMEPAGE = 300  # 5 minutes

# Content Limits
LIMIT_TESTIMONIALS = 3
LIMIT_STATISTICS = 4
LIMIT_ANNOUNCEMENTS = 3
LIMIT_NOTICES = 3  # Additional notices to show in announcements
LIMIT_ANNOUNCEMENTS_TOTAL = 6  # Combined announcements + notices
LIMIT_SERVICES = 3
LIMIT_GALLERY = 6

# Feature Flags
ENABLE_POPUP_NOTICES = True
ENABLE_FEATURED_SERVICES = True
ENABLE_GALLERY_PREVIEW = True

# UI/Display Defaults
DEFAULT_SERVICE_COLOR = 'deuraligreen'
DEFAULT_LOAN_COLOR = 'bhanjyangred'
DEFAULT_FD_COLOR = 'purple'

# Inquiry Types
INQUIRY_TYPE_GENERAL = 'general'
INQUIRY_TYPE_SUPPORT = 'support'
INQUIRY_TYPE_FEEDBACK = 'feedback'

INQUIRY_TYPE_CHOICES = [
    (INQUIRY_TYPE_GENERAL, 'General Inquiry'),
    (INQUIRY_TYPE_SUPPORT, 'Customer Support'),
    (INQUIRY_TYPE_FEEDBACK, 'Feedback'),
]
