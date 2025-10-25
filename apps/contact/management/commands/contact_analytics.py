from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from apps.contact.models import ContactSubmission


class Command(BaseCommand):
    help = 'Generate contact form analytics and reports'

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
            choices=['console', 'file'],
            default='console',
            help='Output format (default: console)'
        )

    def handle(self, *args, **options):
        days = options['days']
        output_format = options['output']
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get submissions in date range
        submissions = ContactSubmission.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Generate analytics
        analytics = self.generate_analytics(submissions, start_date, end_date)
        
        # Output results
        if output_format == 'console':
            self.output_to_console(analytics, days)
        else:
            self.output_to_file(analytics, days)

    def generate_analytics(self, submissions, start_date, end_date):
        """Generate comprehensive analytics"""
        
        # Basic counts
        total_submissions = submissions.count()
        new_submissions = submissions.filter(status='new').count()
        resolved_submissions = submissions.filter(status='resolved').count()
        spam_submissions = submissions.filter(status='spam').count()
        in_progress_submissions = submissions.filter(status='in_progress').count()
        
        # Daily breakdown - Optimized
        from django.db.models.functions import TruncDate
        daily_counts = submissions.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Status breakdown
        status_counts = submissions.values('status').annotate(count=Count('id'))
        
        # Top subjects
        top_subjects = submissions.values('subject').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Attachment statistics
        submissions_with_attachments = submissions.exclude(attachment__isnull=True).exclude(attachment='').count()
        attachment_percentage = (submissions_with_attachments / total_submissions * 100) if total_submissions > 0 else 0
        
        # Response time analysis (for resolved submissions) - Optimized
        resolved_with_times = submissions.filter(
            status='resolved',
            resolved_at__isnull=False
        ).only('created_at', 'resolved_at')  # Only fetch needed fields
        
        # Use database aggregation instead of Python loops
        from django.db.models import F, ExpressionWrapper, fields, Avg
        response_times_agg = resolved_with_times.annotate(
            response_duration=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        ).aggregate(
            avg_response=Avg('response_duration')
        )
        
        avg_response_time = response_times_agg['avg_response']
        avg_response_hours = avg_response_time.total_seconds() / 3600 if avg_response_time else 0
        
        # Spam detection effectiveness
        spam_rate = (spam_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        return {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': (end_date - start_date).days
            },
            'totals': {
                'total_submissions': total_submissions,
                'new_submissions': new_submissions,
                'resolved_submissions': resolved_submissions,
                'spam_submissions': spam_submissions,
                'in_progress_submissions': in_progress_submissions
            },
            'daily_counts': list(daily_counts),
            'status_counts': list(status_counts),
            'top_subjects': list(top_subjects),
            'attachments': {
                'with_attachments': submissions_with_attachments,
                'attachment_percentage': round(attachment_percentage, 2)
            },
            'response_time': {
                'avg_response_hours': round(avg_response_time, 2),
                'resolved_count': len(response_times)
            },
            'spam_rate': round(spam_rate, 2)
        }

    def output_to_console(self, analytics, days):
        """Output analytics to console"""
        self.stdout.write(
            self.style.SUCCESS(f'\nContact Form Analytics - Last {days} Days')
        )
        self.stdout.write('=' * 50)
        
        # Period
        period = analytics['period']
        self.stdout.write(f"Period: {period['start_date']} to {period['end_date']}")
        
        # Totals
        totals = analytics['totals']
        self.stdout.write(f"\nSubmission Totals:")
        self.stdout.write(f"  Total Submissions: {totals['total_submissions']}")
        self.stdout.write(f"  New: {totals['new_submissions']}")
        self.stdout.write(f"  Resolved: {totals['resolved_submissions']}")
        self.stdout.write(f"  In Progress: {totals['in_progress_submissions']}")
        self.stdout.write(f"  Spam: {totals['spam_submissions']}")
        
        # Attachments
        attachments = analytics['attachments']
        self.stdout.write(f"\nAttachments:")
        self.stdout.write(f"  With Attachments: {attachments['with_attachments']}")
        self.stdout.write(f"  Attachment Rate: {attachments['attachment_percentage']}%")
        
        # Response time
        response_time = analytics['response_time']
        self.stdout.write(f"\nResponse Time:")
        self.stdout.write(f"  Average Response Time: {response_time['avg_response_hours']} hours")
        self.stdout.write(f"  Resolved Submissions: {response_time['resolved_count']}")
        
        # Spam rate
        self.stdout.write(f"\nSpam Detection:")
        self.stdout.write(f"  Spam Rate: {analytics['spam_rate']}%")
        
        # Top subjects
        top_subjects = analytics['top_subjects']
        if top_subjects:
            self.stdout.write(f"\nTop Subjects:")
            for subject_data in top_subjects[:5]:
                self.stdout.write(f"  {subject_data['subject']}: {subject_data['count']}")

    def output_to_file(self, analytics, days):
        """Output analytics to file"""
        import json
        from django.conf import settings
        
        filename = f"contact_analytics_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = settings.MEDIA_ROOT / 'reports' / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(analytics, f, indent=2, default=str)
        
        self.stdout.write(
            self.style.SUCCESS(f'Analytics report saved to: {filepath}')
        )
