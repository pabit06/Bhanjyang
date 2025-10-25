#!/usr/bin/env python
"""
Database Backup Management System
"""
import os
import sys
import django
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coop.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from django.core.management.base import BaseCommand

class BackupManager:
    """Manages database and file backups"""
    
    def __init__(self):
        self.backup_dir = Path(settings.BASE_DIR) / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def create_database_backup(self):
        """Create database backup"""
        try:
            backup_file = self.backup_dir / f'database_backup_{self.timestamp}.json'
            
            # Create database dump
            with open(backup_file, 'w', encoding='utf-8') as f:
                call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)
            
            print(f"[SUCCESS] Database backup created: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"[ERROR] Database backup failed: {e}")
            return None
    
    def create_media_backup(self):
        """Create media files backup"""
        try:
            media_backup = self.backup_dir / f'media_backup_{self.timestamp}.zip'
            media_dir = Path(settings.MEDIA_ROOT)
            
            if media_dir.exists():
                with zipfile.ZipFile(media_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(media_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(media_dir)
                            zipf.write(file_path, arcname)
                
                print(f"[SUCCESS] Media backup created: {media_backup}")
                return media_backup
            else:
                print("[INFO] No media directory found")
                return None
        except Exception as e:
            print(f"[ERROR] Media backup failed: {e}")
            return None
    
    def create_static_backup(self):
        """Create static files backup"""
        try:
            static_backup = self.backup_dir / f'static_backup_{self.timestamp}.zip'
            static_dir = Path(settings.STATIC_ROOT)
            
            if static_dir.exists():
                with zipfile.ZipFile(static_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(static_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(static_dir)
                            zipf.write(file_path, arcname)
                
                print(f"[SUCCESS] Static files backup created: {static_backup}")
                return static_backup
            else:
                print("[INFO] No static files directory found")
                return None
        except Exception as e:
            print(f"[ERROR] Static files backup failed: {e}")
            return None
    
    def create_full_backup(self):
        """Create complete system backup"""
        print("Creating full system backup...")
        
        # Create individual backups
        db_backup = self.create_database_backup()
        media_backup = self.create_media_backup()
        static_backup = self.create_static_backup()
        
        # Create combined backup
        full_backup = self.backup_dir / f'full_backup_{self.timestamp}.zip'
        
        try:
            with zipfile.ZipFile(full_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if db_backup and db_backup.exists():
                    zipf.write(db_backup, db_backup.name)
                
                if media_backup and media_backup.exists():
                    zipf.write(media_backup, media_backup.name)
                
                if static_backup and static_backup.exists():
                    zipf.write(static_backup, static_backup.name)
            
            print(f"[SUCCESS] Full backup created: {full_backup}")
            return full_backup
        except Exception as e:
            print(f"[ERROR] Full backup failed: {e}")
            return None
    
    def cleanup_old_backups(self, days=30):
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob('*'):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        backup_file.unlink()
                        removed_count += 1
            
            print(f"[SUCCESS] Removed {removed_count} old backup files")
            return removed_count
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
            return 0
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob('*'):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    file_size = backup_file.stat().st_size
                    backups.append({
                        'name': backup_file.name,
                        'date': file_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'size': f"{file_size / 1024 / 1024:.2f} MB"
                    })
            
            if backups:
                print("\nAvailable Backups:")
                print("-" * 60)
                for backup in sorted(backups, key=lambda x: x['date'], reverse=True):
                    print(f"{backup['name']:<40} {backup['date']:<20} {backup['size']}")
            else:
                print("[INFO] No backups found")
            
            return backups
        except Exception as e:
            print(f"[ERROR] List backups failed: {e}")
            return []

def main():
    """Main backup management function"""
    backup_manager = BackupManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'database':
            backup_manager.create_database_backup()
        elif command == 'media':
            backup_manager.create_media_backup()
        elif command == 'static':
            backup_manager.create_static_backup()
        elif command == 'full':
            backup_manager.create_full_backup()
        elif command == 'cleanup':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            backup_manager.cleanup_old_backups(days)
        elif command == 'list':
            backup_manager.list_backups()
        else:
            print("Usage: python backup_manager.py [database|media|static|full|cleanup|list]")
    else:
        # Default: create full backup
        backup_manager.create_full_backup()

if __name__ == '__main__':
    main()
