"""
CDN integration utilities for downloads app.
Supports CloudFront, Cloudflare, and custom CDN providers.
"""
import logging
from typing import Optional
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class CDNManager:
    """Manages CDN URLs for downloadable files"""
    
    @staticmethod
    def get_cdn_url(file_url: str, file_obj=None) -> str:
        """
        Get CDN URL for a file if CDN is enabled and file is public.
        
        Args:
            file_url: Original file URL
            file_obj: DownloadableFile instance (optional)
            
        Returns:
            str: CDN URL if enabled and applicable, otherwise original URL
        """
        downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
        
        # Check if CDN is enabled
        if not downloads_settings.get('ENABLE_CDN', False):
            return file_url
        
        # Check if file should use CDN (public files only)
        if file_obj:
            # Only use CDN for public files (not login-required)
            if file_obj.requires_login:
                return file_url
            
            # Check if file is frequently downloaded (optional optimization)
            min_downloads = downloads_settings.get('CDN_MIN_DOWNLOADS', 10)
            if file_obj.download_count < min_downloads:
                return file_url
        
        # Get CDN base URL
        cdn_base_url = downloads_settings.get('CDN_BASE_URL', '')
        if not cdn_base_url:
            return file_url
        
        # Remove trailing slash from CDN base URL
        cdn_base_url = cdn_base_url.rstrip('/')
        
        # Extract path from file URL
        if file_url.startswith('http://') or file_url.startswith('https://'):
            # Full URL - extract path
            from urllib.parse import urlparse
            parsed = urlparse(file_url)
            file_path = parsed.path
        else:
            # Relative URL - use as is
            file_path = file_url.lstrip('/')
        
        # Construct CDN URL
        cdn_url = f"{cdn_base_url}/{file_path}"
        
        logger.debug(f"CDN URL generated: {cdn_url} (original: {file_url})")
        return cdn_url
    
    @staticmethod
    def get_secure_download_url(file_obj, request=None) -> str:
        """
        Get secure download URL (through Django view) with optional CDN.
        
        For public files, returns CDN URL if enabled.
        For protected files, always returns Django view URL.
        
        Args:
            file_obj: DownloadableFile instance
            request: HttpRequest instance (optional)
            
        Returns:
            str: URL for downloading the file
        """
        downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
        
        # Protected files always go through Django view
        if file_obj.requires_login:
            from django.urls import reverse
            if request:
                return request.build_absolute_uri(
                    reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
                )
            else:
                return reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
        
        # Public files can use CDN if enabled
        if downloads_settings.get('ENABLE_CDN', False):
            # For CDN, we still need to go through Django for tracking
            # But we can optimize by serving from CDN in the view
            from django.urls import reverse
            if request:
                return request.build_absolute_uri(
                    reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
                )
            else:
                return reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
        
        # No CDN - use Django view
        from django.urls import reverse
        if request:
            return request.build_absolute_uri(
                reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
            )
        else:
            return reverse('downloads:serve_file', kwargs={'pk': file_obj.pk})
    
    @staticmethod
    def is_cdn_enabled() -> bool:
        """Check if CDN is enabled in settings"""
        downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
        return downloads_settings.get('ENABLE_CDN', False)
    
    @staticmethod
    def get_cdn_provider() -> Optional[str]:
        """Get CDN provider name from settings"""
        downloads_settings = getattr(settings, 'DOWNLOADS_SETTINGS', {})
        return downloads_settings.get('CDN_PROVIDER', None)
