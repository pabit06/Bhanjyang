# downloads/admin.py
# (No changes needed if you already have this, just ensure the model is registered)

from django.contrib import admin
from .models import Download

@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_at')
    search_fields = ('title', 'description')
    list_filter = ('file_type', 'uploaded_at')