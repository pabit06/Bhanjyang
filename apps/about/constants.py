"""
Constants for the About app.

Centralizes magic strings, default values, and configuration constants
to improve maintainability and reduce duplication.
"""
from django.utils.translation import gettext_lazy as _

# =============================================================================
# RTI (Right to Information) Act 2064 Constants
# =============================================================================

# Default RTI email address
DEFAULT_RTI_EMAIL = 'rti@bhanjyang.coop.np'

# RTI Act 2064 help texts
RTI_HELP_TEXTS = {
    'information_officer': _('Designate this staff member as the Information Officer under RTI Act 2064'),
    'rti_email': _('Dedicated email for RTI requests (e.g., rti@bhanjyang.coop.np)'),
}

# =============================================================================
# Cache Configuration Constants
# =============================================================================

# Cache timeout in seconds
CACHE_TIMEOUT_SHORT = 60  # 1 minute
CACHE_TIMEOUT_DEFAULT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 600  # 10 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour
CACHE_TIMEOUT_DAY = 86400  # 24 hours

# Cache key prefixes
CACHE_KEY_PREFIX_ABOUT = 'about'
CACHE_KEY_PREFIX_TEAM = 'team'
CACHE_KEY_PREFIX_COOPERATIVE = 'cooperative'

# =============================================================================
# Model Choice Constants
# =============================================================================

# Event types for CooperativeTimeline
EVENT_TYPE_MILESTONE = 'milestone'
EVENT_TYPE_ACHIEVEMENT = 'achievement'
EVENT_TYPE_EXPANSION = 'expansion'
EVENT_TYPE_AWARD = 'award'
EVENT_TYPE_PARTNERSHIP = 'partnership'
EVENT_TYPE_OTHER = 'other'

# Statistic types for CooperativeStatistic
STATISTIC_TYPE_MEMBERS = 'members'
STATISTIC_TYPE_DEPOSITS = 'deposits'
STATISTIC_TYPE_LOANS = 'loans'
STATISTIC_TYPE_BRANCHES = 'branches'
STATISTIC_TYPE_EMPLOYEES = 'employees'
STATISTIC_TYPE_ASSETS = 'assets'
STATISTIC_TYPE_OTHER = 'other'

# Affiliation types for CooperativeAffiliation
AFFILIATION_TYPE_REGULATORY = 'regulatory'
AFFILIATION_TYPE_ASSOCIATION = 'association'
AFFILIATION_TYPE_PARTNERSHIP = 'partnership'
AFFILIATION_TYPE_CERTIFICATION = 'certification'
AFFILIATION_TYPE_UMBRELLA = 'umbrella'
AFFILIATION_TYPE_COOPERATIVE_BANK = 'cooperative_bank'
AFFILIATION_TYPE_OTHER = 'other'

# Message types for LeadershipMessage
MESSAGE_TYPE_CHAIRMAN = 'chairman'
MESSAGE_TYPE_MANAGER = 'manager'
MESSAGE_TYPE_DIRECTOR = 'director'
MESSAGE_TYPE_OTHER = 'other'

# Position choices for Membership
POSITION_CHAIRMAN = 'chairman'
POSITION_VICE_CHAIRMAN = 'vice_chairman'
POSITION_SECRETARY = 'secretary'
POSITION_TREASURER = 'treasurer'
POSITION_MEMBER = 'member'
POSITION_COORDINATOR = 'coordinator'
POSITION_OTHER = 'other'

# =============================================================================
# Display/UI Constants
# =============================================================================

# Default color theme
DEFAULT_COLOR_THEME = 'deuraligreen'

# Pagination defaults
DEFAULT_PAGE_SIZE = 12
DEFAULT_TIMELINE_LIMIT = 6

# =============================================================================
# File Upload Paths
# =============================================================================

UPLOAD_PATH_COOPERATIVE = 'about/cooperative/'
UPLOAD_PATH_TIMELINE = 'about/timeline/'
UPLOAD_PATH_AFFILIATIONS = 'about/affiliations/'
UPLOAD_PATH_LEADERSHIP = 'about/leadership/'
UPLOAD_PATH_TEAM_PHOTOS = 'about/team/photos/'
UPLOAD_PATH_COMMITTEES = 'about/committees/'

# =============================================================================
# Error Messages
# =============================================================================

ERROR_UNABLE_TO_LOAD = _('Unable to load content')
ERROR_PERSON_REQUIRED = _('Either select a person or enter a name.')
ERROR_POSITION_REQUIRED = _('Please select a position.')
ERROR_CUSTOM_POSITION_REQUIRED = _("Custom position must be provided when 'Other' is selected.")

