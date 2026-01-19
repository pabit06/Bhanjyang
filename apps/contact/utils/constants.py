"""
Constants for the Contact app.
"""

# File Upload Constants
MAX_CONTACT_FILE_SIZE_MB = 5
MAX_CONTACT_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

ALLOWED_CONTACT_FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
ALLOWED_CONTACT_FILE_EXTENSIONS_WITH_DOT = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']

ALLOWED_CONTACT_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png'
]

# KYM Form File Constants
ALLOWED_KYM_FILE_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
ALLOWED_KYM_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']

# Form Field Limits
MAX_NAME_LENGTH = 100
MIN_NAME_LENGTH = 2
MAX_EMAIL_LENGTH = 254
MAX_PHONE_LENGTH = 20
MIN_PHONE_LENGTH = 7
MAX_SUBJECT_LENGTH = 200
MIN_SUBJECT_LENGTH = 3
MIN_MESSAGE_LENGTH = 10

# Time Constants
SECONDS_IN_24_HOURS = 86400
SUBMISSION_CLEANUP_DAYS = 365

# Rate Limiting
CONTACT_FORM_RATE_LIMIT_PER_IP = '5/m'  # 5 requests per minute
CONTACT_FORM_RATE_LIMIT_PER_EMAIL = '3/h'  # 3 requests per hour

# Form CSS Classes
FORM_INPUT_CSS = (
    'w-full px-4 py-3 rounded-lg border-2 border-gray-300 '
    'focus:ring-2 focus:ring-deuraligreen/50 focus:border-deuraligreen '
    'bg-white transition-all duration-200'
)

KYM_INPUT_CSS = (
    'w-full pl-10 pr-4 py-3 rounded-lg border-2 border-gray-300 '
    'focus:outline-none focus:border-deuraligreen transition-colors duration-200'
)

# Spam Detection
DISPOSABLE_EMAIL_DOMAINS = frozenset([
    '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
    'mailinator.com', 'getnada.com'
])

# Comprehensive spam patterns (merged from spam_detector.py)
SPAM_PATTERNS = [
    # Original patterns
    r'Click here:', r'free money', r'Win \$1000 prize',
    # Additional spam keywords
    r'\bcasino\b', r'\bviagra\b', r'\bcryptocurrency\b', r'\bbitcoin\b',
    r'\binvestment\b', r'\blottery\b', r'\bprize\b', r'\bwinner\b',
    r'\bclick here\b', r'\bbuy now\b', r'\bseo ranking\b',
    r'\bmarketing service\b', r'\bdating\b', r'\bsingles\b',
    # Excessive links (3 or more http/https)
    r'(https?://.*?){3,}'
]

# Validation Thresholds
MAX_DOMAIN_DIGITS = 5
MIN_LOCAL_PART_LETTERS = 2
MIN_LOCAL_PART_DIGITS_FOR_SUSPICION = 5
MAX_WORD_REPETITION_RATIO = 0.4

