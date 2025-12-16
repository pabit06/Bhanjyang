# downloads/management/commands/download_analytics.py

from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from apps.downloads.models import DownloadableFile
from apps.downloads.performance import DownloadsQueryOptimizer
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate comprehensive download analytics and reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)'
        )
        parser.add_argument(
            '--output',
            type=str,
            choices=['console', 'file', 'json'],
            default='console',
            help='Output format (default: console)'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Output file path (required if output=file)'
        )

    def handle(self, *args, **options):
        days = options['days']
        output_format = options['output']
        output_file = options['file']
        
        self.stdout.write(f"Generating download analytics for the last {days} days...")
        
        # Generate analytics data
        analytics_data = self.generate_analytics(days)
        
        # Output results
        if output_format == 'console':
            self.output_to_console(analytics_data)
        elif output_format == 'file':
            if not output_file:
                self.stderr.write("Error: --file argument required when output=file")
                return
            self.output_to_file(analytics_data, output_file)
        elif output_format == 'json':
            self.output_to_json(analytics_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated analytics for {days} days')
        )

    def generate_analytics(self, days):
        """Generate comprehensive analytics data"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Basic statistics
        basic_stats = DownloadsQueryOptimizer.get_file_statistics()
        
        # Category analytics
        category_stats = DownloadsQueryOptimizer.get_category_statistics()
        
        # Popular files
        popular_files = DownloadsQueryOptimizer.get_popular_files(limit=10)
        
        # Download trends
        download_trends = DownloadsQueryOptimizer.get_download_trends(days)
        
        # User patterns
        user_patterns = DownloadsQueryOptimizer.get_user_download_patterns()
        
        # Performance metrics
        performance_metrics = self.get_performance_metrics()
        
        # Security metrics
        security_metrics = self.get_security_metrics()
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'basic_stats': basic_stats,
            'category_stats': category_stats,
            'popular_files': [
                {
                    'id': file.id,
                    'title': file.title,
                    'category': file.get_category_display(),
                    'download_count': file.download_count,
                    'view_count': file.view_count,
                    'file_type': file.file_type,
                    'file_size': file.file_size
                }
                for file in popular_files
            ],
            'download_trends': download_trends,
            'user_patterns': user_patterns,
            'performance_metrics': performance_metrics,
            'security_metrics': security_metrics
        }

    def get_performance_metrics(self):
        """Get performance-related metrics"""
        # Calculate average file size manually
        total_size = 0
        file_count = 0
        
        for file_obj in DownloadableFile.objects.all():
            try:
                if file_obj.file and hasattr(file_obj.file, 'size'):
                    total_size += file_obj.file.size
                    file_count += 1
            except:
                continue
        
        avg_file_size = total_size / file_count if file_count > 0 else 0
        
        # Files by size category
        size_categories = {
            'small': 0,
            'medium': 0,
            'large': 0
        }
        
        for file_obj in DownloadableFile.objects.all():
            try:
                if file_obj.file and hasattr(file_obj.file, 'size'):
                    size = file_obj.file.size
                    if size < 1024*1024:
                        size_categories['small'] += 1
                    elif size < 10*1024*1024:
                        size_categories['medium'] += 1
                    else:
                        size_categories['large'] += 1
            except:
                continue
        
        # Access patterns
        recent_access = DownloadableFile.objects.filter(
            last_accessed__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return {
            'avg_file_size_mb': round(avg_file_size / (1024*1024), 2) if avg_file_size else 0,
            'size_categories': size_categories,
            'recent_access_count': recent_access,
            'total_storage_mb': self.calculate_total_storage()
        }

    def get_security_metrics(self):
        """Get security-related metrics"""
        # Files with hash verification
        files_with_hash = DownloadableFile.objects.exclude(file_hash='').count()
        
        # Login required files
        login_required = DownloadableFile.objects.filter(requires_login=True).count()
        
        # Expired files
        expired_files = DownloadableFile.objects.filter(
            expires_at__lt=timezone.now()
        ).count()
        
        # Files by uploader
        uploader_stats = DownloadableFile.objects.values('uploaded_by__username').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'files_with_hash': files_with_hash,
            'login_required_count': login_required,
            'expired_files_count': expired_files,
            'top_uploaders': list(uploader_stats)
        }

    def calculate_total_storage(self):
        """Calculate total storage used by files"""
        total_size = 0
        for file_obj in DownloadableFile.objects.all():
            try:
                if file_obj.file and hasattr(file_obj.file, 'size'):
                    total_size += file_obj.file.size
            except:
                continue
        return round(total_size / (1024*1024), 2)  # Convert to MB

    def output_to_console(self, data):
        """Output analytics to console"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DOWNLOAD ANALYTICS REPORT")
        self.stdout.write("="*60)
        
        # Basic stats
        self.stdout.write(f"\nBASIC STATISTICS")
        self.stdout.write(f"Total Files: {data['basic_stats'].get('total_files', 0)}")
        self.stdout.write(f"Active Files: {data['basic_stats'].get('active_files', 0)}")
        self.stdout.write(f"Featured Files: {data['basic_stats'].get('featured_files', 0)}")
        self.stdout.write(f"Total Downloads: {data['basic_stats'].get('total_downloads', 0)}")
        self.stdout.write(f"Total Views: {data['basic_stats'].get('total_views', 0)}")
        
        # Category breakdown
        self.stdout.write(f"\nCATEGORY BREAKDOWN")
        for category in data['category_stats']:
            self.stdout.write(f"{category['category']}: {category['count']} files")
        
        # Popular files
        self.stdout.write(f"\nTOP 5 POPULAR FILES")
        for i, file in enumerate(data['popular_files'][:5], 1):
            self.stdout.write(f"{i}. {file['title']} ({file['download_count']} downloads)")
        
        # Performance metrics
        self.stdout.write(f"\nPERFORMANCE METRICS")
        self.stdout.write(f"Average File Size: {data['performance_metrics']['avg_file_size_mb']} MB")
        self.stdout.write(f"Total Storage Used: {data['performance_metrics']['total_storage_mb']} MB")
        self.stdout.write(f"Files Accessed Recently: {data['performance_metrics']['recent_access_count']}")
        
        # Security metrics
        self.stdout.write(f"\nSECURITY METRICS")
        self.stdout.write(f"Files with Hash Verification: {data['security_metrics']['files_with_hash']}")
        self.stdout.write(f"Login Required Files: {data['security_metrics']['login_required_count']}")
        self.stdout.write(f"Expired Files: {data['security_metrics']['expired_files_count']}")

    def output_to_file(self, data, file_path):
        """Output analytics to file"""
        with open(file_path, 'w') as f:
            f.write("DOWNLOAD ANALYTICS REPORT\n")
            f.write("="*60 + "\n\n")
            
            # Basic stats
            f.write("BASIC STATISTICS\n")
            f.write("-"*20 + "\n")
            f.write(f"Total Files: {data['basic_stats'].get('total_files', 0)}\n")
            f.write(f"Active Files: {data['basic_stats'].get('active_files', 0)}\n")
            f.write(f"Featured Files: {data['basic_stats'].get('featured_files', 0)}\n")
            f.write(f"Total Downloads: {data['basic_stats'].get('total_downloads', 0)}\n")
            f.write(f"Total Views: {data['basic_stats'].get('total_views', 0)}\n\n")
            
            # Category breakdown
            f.write("CATEGORY BREAKDOWN\n")
            f.write("-"*20 + "\n")
            for category in data['category_stats']:
                f.write(f"{category['category']}: {category['count']} files\n")
            f.write("\n")
            
            # Popular files
            f.write("TOP 10 POPULAR FILES\n")
            f.write("-"*20 + "\n")
            for i, file in enumerate(data['popular_files'], 1):
                f.write(f"{i}. {file['title']} ({file['download_count']} downloads)\n")
            f.write("\n")
            
            # Performance metrics
            f.write("PERFORMANCE METRICS\n")
            f.write("-"*20 + "\n")
            f.write(f"Average File Size: {data['performance_metrics']['avg_file_size_mb']} MB\n")
            f.write(f"Total Storage Used: {data['performance_metrics']['total_storage_mb']} MB\n")
            f.write(f"Files Accessed Recently: {data['performance_metrics']['recent_access_count']}\n")
            f.write(f"Small Files (<1MB): {data['performance_metrics']['size_categories']['small']}\n")
            f.write(f"Medium Files (1-10MB): {data['performance_metrics']['size_categories']['medium']}\n")
            f.write(f"Large Files (>10MB): {data['performance_metrics']['size_categories']['large']}\n\n")
            
            # Security metrics
            f.write("SECURITY METRICS\n")
            f.write("-"*20 + "\n")
            f.write(f"Files with Hash Verification: {data['security_metrics']['files_with_hash']}\n")
            f.write(f"Login Required Files: {data['security_metrics']['login_required_count']}\n")
            f.write(f"Expired Files: {data['security_metrics']['expired_files_count']}\n")
        
        self.stdout.write(f"Analytics report saved to: {file_path}")

    def output_to_json(self, data):
        """Output analytics as JSON"""
        json_output = json.dumps(data, indent=2, default=str)
        self.stdout.write(json_output)
