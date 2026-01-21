"""
Celery tasks for downloads app.
Handles asynchronous operations like bulk download ZIP creation.
"""
import os
import logging
import zipfile
import tempfile
from typing import List, Tuple, Optional
from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import DownloadableFile
from .services import BulkDownloadService
from .security import AccessControlManager

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, name='downloads.create_bulk_download_zip')
def create_bulk_download_zip_task(
    self,
    file_ids: List[int],
    user_id: Optional[int] = None,
    notification_email: Optional[str] = None
) -> dict:
    """
    Asynchronously create a ZIP file containing multiple downloadable files.
    
    Args:
        file_ids: List of file IDs to include in ZIP
        user_id: ID of user requesting the download (optional)
        notification_email: Email address to notify when ZIP is ready (optional)
        
    Returns:
        dict: Task result with status, file_path, and download_url
    """
    try:
        # Get user if provided
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                logger.warning(f"User ID {user_id} not found for bulk download task")
        
        # Get accessible files
        downloadable_files = BulkDownloadService.get_accessible_files(user, file_ids)
        
        if not downloadable_files:
            logger.warning(f"No accessible files found for bulk download task")
            return {
                'status': 'error',
                'message': 'No accessible files found',
                'file_ids': file_ids
            }
        
        # Create ZIP file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        success_count = 0
        failed_files = []
        
        try:
            with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_obj in downloadable_files:
                    try:
                        # Add file to ZIP
                        zip_file.write(file_obj.file.path, file_obj.file.name)
                        success_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to add file {file_obj.id} to ZIP: {e}")
                        failed_files.append(file_obj.id)
                        continue
            
            # Save ZIP to storage
            zip_filename = f"bulk_downloads_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
            with open(temp_file.name, 'rb') as zip_file:
                saved_path = default_storage.save(
                    f'downloads/bulk/{zip_filename}',
                    ContentFile(zip_file.read())
                )
            
            # Get download URL
            download_url = default_storage.url(saved_path)
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            # Send notification if email provided
            if notification_email:
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    subject = 'Your bulk download is ready'
                    message = f'''
Your bulk download containing {success_count} file(s) is ready.

Download URL: {download_url}
Created at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: This download link will expire after 24 hours.
'''
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [notification_email],
                        fail_silently=False,
                    )
                    logger.info(f"Notification email sent to {notification_email}")
                except Exception as e:
                    logger.error(f"Failed to send notification email: {e}", exc_info=True)
            
            logger.info(
                f"Bulk download ZIP created successfully: {saved_path} "
                f"({success_count} files, {len(failed_files)} failed)"
            )
            
            return {
                'status': 'success',
                'file_path': saved_path,
                'download_url': download_url,
                'success_count': success_count,
                'failed_files': failed_files,
                'created_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise
            
    except Exception as e:
        logger.error(f"Bulk download ZIP creation failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e),
            'file_ids': file_ids
        }


@shared_task(name='downloads.cleanup_old_bulk_downloads')
def cleanup_old_bulk_downloads_task(days: int = 1) -> dict:
    """
    Clean up old bulk download ZIP files from storage.
    
    Args:
        days: Delete files older than this many days (default: 1 day)
        
    Returns:
        dict: Cleanup result with count of deleted files
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        deleted_count = 0
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # List files in bulk downloads directory
        bulk_dir = 'downloads/bulk/'
        if default_storage.exists(bulk_dir):
            files = default_storage.listdir(bulk_dir)[1]  # Get files only
            
            for filename in files:
                file_path = os.path.join(bulk_dir, filename)
                try:
                    # Check file modification time
                    modified_time = default_storage.get_modified_time(file_path)
                    if modified_time < cutoff_date:
                        default_storage.delete(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old bulk download: {file_path}")
                except Exception as e:
                    logger.warning(f"Error deleting {file_path}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} old bulk download files")
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Bulk download cleanup failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }
