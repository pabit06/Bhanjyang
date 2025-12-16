"""
Constants for the Contact app.
"""

# File Upload Constants
MAX_CONTACT_FILE_SIZE_MB = 5
MAX_CONTACT_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

ALLOWED_CONTACT_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']

ALLOWED_CONTACT_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png'
]

# KYM Form File Constants
ALLOWED_KYM_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']

# Form Field Limits
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 254
MAX_PHONE_LENGTH = 20
MAX_SUBJECT_LENGTH = 200
MIN_MESSAGE_LENGTH = 10

# Rate Limiting (when implemented)
CONTACT_FORM_RATE_LIMIT_PER_IP = '5/m'  # 5 requests per minute
CONTACT_FORM_RATE_LIMIT_PER_EMAIL = '3/h'  # 3 requests per hour

