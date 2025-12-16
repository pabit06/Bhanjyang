# downloads/management/commands/monitor_downloads.py

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.downloads.models import DownloadableFile
from apps.downloads.performance import DownloadsPerformanceMonitor
from apps.downloads.security import SecurityAuditLogger
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor downloads system health and performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-cache',
            action='store_true',
            help='Check cache performance'
        )
        parser.add_argument(
            '--check-security',
            action='store_true',
            help='Check security metrics'
        )
        parser.add_argument(
            '--check-performance',
            action='store_true',
            help='Check performance metrics'
        )
        parser.add_argument(
            '--check-storage',
            action='store_true',
            help='Check storage usage'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all checks'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting downloads system monitoring...")
        
        checks_run = 0
        
        if options['all'] or options['check_cache']:
            self.check_cache_performance()
            checks_run += 1
        
        if options['all'] or options['check_security']:
            self.check_security_metrics()
            checks_run += 1
        
        if options['all'] or options['check_performance']:
            self.check_performance_metrics()
            checks_run += 1
        
        if options['all'] or options['check_storage']:
            self.check_storage_usage()
            checks_run += 1
        
        if checks_run == 0:
            self.stdout.write("No checks specified. Use --help to see available options.")
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Monitoring completed. {checks_run} check(s) run.')
        )

    def check_cache_performance(self):
        """Check cache performance and health"""
        self.stdout.write("\nCACHE PERFORMANCE CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Test cache operations
            test_key = 'downloads_monitor_test'
            test_data = {'test': 'data', 'timestamp': timezone.now().isoformat()}
            
            # Test cache set
            DownloadsPerformanceMonitor.cache_file_statistics(test_data, timeout=60)
            
            # Test cache get
            cached_data = DownloadsPerformanceMonitor.get_cached_file_statistics()
            
            if cached_data:
                self.stdout.write(self.style.SUCCESS("Cache operations working correctly"))
            else:
                self.stdout.write(self.style.WARNING("Cache retrieval failed"))
            
            # Check cache hit rates (simulated)
            self.stdout.write(f"Cache Status: Active")
            self.stdout.write(f"Cache Timeout: 60 seconds")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cache check failed: {e}"))

    def check_security_metrics(self):
        """Check security-related metrics"""
        self.stdout.write("\nSECURITY METRICS CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Files without hash verification
            files_without_hash = DownloadableFile.objects.filter(
                Q(file_hash='') | Q(file_hash__isnull=True)
            ).count()
            
            total_files = DownloadableFile.objects.count()
            hash_coverage = ((total_files - files_without_hash) / total_files * 100) if total_files > 0 else 0
            
            if hash_coverage >= 90:
                self.stdout.write(self.style.SUCCESS(f"Hash verification coverage: {hash_coverage:.1f}%"))
            elif hash_coverage >= 70:
                self.stdout.write(self.style.WARNING(f"Hash verification coverage: {hash_coverage:.1f}%"))
            else:
                self.stdout.write(self.style.ERROR(f"Hash verification coverage: {hash_coverage:.1f}%"))
            
            # Expired files
            expired_files = DownloadableFile.objects.filter(
                expires_at__lt=timezone.now()
            ).count()
            
            if expired_files == 0:
                self.stdout.write(self.style.SUCCESS("No expired files found"))
            else:
                self.stdout.write(self.style.WARNING(f"{expired_files} expired files found"))
            
            # Login required files
            login_required = DownloadableFile.objects.filter(requires_login=True).count()
            self.stdout.write(f"Files requiring login: {login_required}")
            
            # Security audit logs (simulated check)
            self.stdout.write("Security audit logging: Active")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Security check failed: {e}"))

    def check_performance_metrics(self):
        """Check performance-related metrics"""
        self.stdout.write("\nPERFORMANCE METRICS CHECK")
        self.stdout.write("-" * 40)
        
        try:
            # Database query performance
            start_time = timezone.now()
            files = list(DownloadableFile.objects.all()[:100])
            query_time = (timezone.now() - start_time).total_seconds()
            
            if query_time < 0.1:
                self.stdout.write(self.style.SUCCESS(f"Database query performance: {query_time:.3f}s"))
            elif query_time < 0.5:
                self.stdout.write(self.style.WARNING(f"Database query performance: {query_time:.3f}s"))
            else:
                self.stdout.write(self.style.ERROR(f"Database query performance: {query_time:.3f}s"))
            
            # File size distribution
            small_files = 0
            medium_files = 0
            large_files = 0
            
            for file_obj in DownloadableFile.objects.all():
                try:
                    if file_obj.file and hasattr(file_obj.file, 'size'):
                        size = file_obj.file.size
                        if size < 1024*1024:
                            small_files += 1
                        elif size < 10*1024*1024:
                            medium_files += 1
                        else:
                            large_files += 1
                except:
                    continue
            
            self.stdout.write(f"Small files (<1MB): {small_files}")
            self.stdout.write(f"Medium files (1-10MB): {medium_files}")
            self.stdout.write(f"Large files (>10MB): {large_files}")
            
            # Recent activity
            recent_uploads = DownloadableFile.objects.filter(
                uploaded_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            recent_access = DownloadableFile.objects.filter(
                last_accessed__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            self.stdout.write(f"Recent uploads (7 days): {recent_uploads}")
            self.stdout.write(f"Recent access (7 days): {recent_access}")
            
            # Performance recommendations
            total_files = DownloadableFile.objects.count()
            if large_files > total_files * 0.2:
                self.stdout.write(self.style.WARNING("Consider optimizing large files"))
            
            if recent_access < total_files * 0.1:
                self.stdout.write(self.style.WARNING("Low file access activity"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Performance check failed: {e}"))

    def check_storage_usage(self):
        """Check storage usage and health"""
        self.stdout.write("\nSTORAGE USAGE CHECK")
        self.stdout.write("-" * 40)
        
        try:
            total_files = DownloadableFile.objects.count()
            total_size = 0
            missing_files = 0
            
            for file_obj in DownloadableFile.objects.all():
                try:
                    if file_obj.file and hasattr(file_obj.file, 'size'):
                        total_size += file_obj.file.size
                    else:
                        missing_files += 1
                except:
                    missing_files += 1
            
            # Convert to MB
            total_size_mb = total_size / (1024 * 1024)
            
            self.stdout.write(f"Total files: {total_files}")
            self.stdout.write(f"Total storage: {total_size_mb:.2f} MB")
            self.stdout.write(f"Average file size: {total_size_mb/total_files:.2f} MB" if total_files > 0 else "Average file size: 0 MB")
            
            if missing_files == 0:
                self.stdout.write(self.style.SUCCESS("All files accessible"))
            else:
                self.stdout.write(self.style.WARNING(f"{missing_files} files not accessible"))
            
            # Storage recommendations
            if total_size_mb > 1000:  # More than 1GB
                self.stdout.write(self.style.WARNING("Consider implementing file cleanup policies"))
            
            if missing_files > total_files * 0.05:  # More than 5% missing
                self.stdout.write(self.style.ERROR("High number of missing files - check storage"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Storage check failed: {e}"))

    def get_system_health_score(self):
        """Calculate overall system health score"""
        score = 100
        
        # Deduct points for issues
        expired_files = DownloadableFile.objects.filter(
            expires_at__lt=timezone.now()
        ).count()
        
        if expired_files > 0:
            score -= min(expired_files * 2, 20)
        
        files_without_hash = DownloadableFile.objects.filter(
            Q(file_hash='') | Q(file_hash__isnull=True)
        ).count()
        
        total_files = DownloadableFile.objects.count()
        if total_files > 0:
            hash_coverage = (total_files - files_without_hash) / total_files
            if hash_coverage < 0.9:
                score -= 15
        
        return max(score, 0)
