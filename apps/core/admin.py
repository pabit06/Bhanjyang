from .security_admin import APIKeyAdmin, SecurityLogAdmin
from apps.admin.admin_site import admin_site
from .models import APIKey, SecurityLog
from django.contrib.auth.models import User, Group

# Register auth models
admin_site.register(User)
admin_site.register(Group)

# Register core models
admin_site.register(APIKey, APIKeyAdmin)
admin_site.register(SecurityLog, SecurityLogAdmin)
