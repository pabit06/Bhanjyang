from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
import hashlib
from .models import slugify_nepali  # Importing helper function from same module (will be available after file placement, actually I am appending so I can use it directly)

# ... (Existing imports will be there, I will append this code)
