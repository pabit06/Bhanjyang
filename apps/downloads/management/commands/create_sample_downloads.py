# downloads/management/commands/create_sample_downloads.py

from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta
from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel


class Command(BaseCommand):
    help = 'Create sample downloadable files with different priorities and categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing sample data...')
            DownloadableFile.objects.all().delete()

        self.stdout.write('Creating sample downloadable files...')

        # Sample files data
        sample_files = [
            {
                'title': 'Membership Application Form',
                'description': 'Complete membership application form for new members. Please fill out all required fields and submit with necessary documents.',
                'category': FileCategory.FORM,
                'priority': PriorityLevel.HIGH,
                'is_featured': True,
                'requires_login': False,
                'tags': 'membership, application, form, new member',
                'file_content': b'PDF content for membership form',
                'file_name': 'membership_application.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Annual Financial Report 2024',
                'description': 'Comprehensive annual financial report including income statements, balance sheets, and audit findings.',
                'category': FileCategory.REPORT,
                'priority': PriorityLevel.URGENT,
                'is_featured': True,
                'requires_login': True,
                'tags': 'financial, report, annual, audit, 2024',
                'file_content': b'PDF content for financial report',
                'file_name': 'annual_report_2024.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Cooperative Bylaws and Policies',
                'description': 'Complete set of cooperative bylaws, policies, and procedures governing member rights and responsibilities.',
                'category': FileCategory.POLICY,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': False,
                'requires_login': False,
                'tags': 'bylaws, policies, procedures, governance',
                'file_content': b'PDF content for bylaws',
                'file_name': 'cooperative_bylaws.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Loan Application Form',
                'description': 'Application form for various loan products offered by the cooperative. Includes personal and business loan options.',
                'category': FileCategory.FORM,
                'priority': PriorityLevel.HIGH,
                'is_featured': True,
                'requires_login': False,
                'tags': 'loan, application, personal, business, credit',
                'file_content': b'PDF content for loan application',
                'file_name': 'loan_application.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Monthly Newsletter - December 2024',
                'description': 'Latest monthly newsletter featuring cooperative updates, member spotlights, and upcoming events.',
                'category': FileCategory.PUBLICATION,
                'priority': PriorityLevel.LOW,
                'is_featured': False,
                'requires_login': False,
                'tags': 'newsletter, monthly, updates, events, december',
                'file_content': b'PDF content for newsletter',
                'file_name': 'newsletter_dec_2024.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'User Manual - Online Banking',
                'description': 'Comprehensive user manual for online banking services. Includes step-by-step instructions and troubleshooting guide.',
                'category': FileCategory.MANUAL,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': False,
                'requires_login': False,
                'tags': 'manual, online banking, guide, instructions, tutorial',
                'file_content': b'PDF content for user manual',
                'file_name': 'online_banking_manual.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Certificate of Membership',
                'description': 'Official certificate template for new members. This document confirms membership status in the cooperative.',
                'category': FileCategory.CERTIFICATE,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': False,
                'requires_login': True,
                'tags': 'certificate, membership, official, template',
                'file_content': b'PDF content for certificate',
                'file_name': 'membership_certificate.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Cooperative Services Brochure',
                'description': 'Informative brochure highlighting all services offered by the cooperative including savings, loans, and insurance.',
                'category': FileCategory.BROCHURE,
                'priority': PriorityLevel.LOW,
                'is_featured': False,
                'requires_login': False,
                'tags': 'brochure, services, savings, loans, insurance',
                'file_content': b'PDF content for brochure',
                'file_name': 'services_brochure.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Emergency Contact Information',
                'description': 'Important emergency contact information and procedures for members during crisis situations.',
                'category': FileCategory.OTHER,
                'priority': PriorityLevel.URGENT,
                'is_featured': True,
                'requires_login': False,
                'tags': 'emergency, contact, crisis, procedures, important',
                'file_content': b'PDF content for emergency info',
                'file_name': 'emergency_contacts.pdf',
                'content_type': 'application/pdf'
            },
            {
                'title': 'Quarterly Financial Statement Q4 2024',
                'description': 'Fourth quarter financial statement showing cooperative performance and member benefits.',
                'category': FileCategory.REPORT,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': False,
                'requires_login': True,
                'tags': 'quarterly, financial, statement, Q4, 2024',
                'file_content': b'PDF content for quarterly report',
                'file_name': 'q4_financial_statement.pdf',
                'content_type': 'application/pdf'
            }
        ]

        created_count = 0
        for file_data in sample_files:
            # Create file upload
            uploaded_file = SimpleUploadedFile(
                file_data['file_name'],
                file_data['file_content'],
                content_type=file_data['content_type']
            )

            # Set expiration date for some files
            expires_at = None
            if file_data['priority'] == PriorityLevel.URGENT:
                expires_at = timezone.now() + timedelta(days=30)  # Urgent files expire in 30 days
            elif file_data['category'] == FileCategory.REPORT:
                expires_at = timezone.now() + timedelta(days=365)  # Reports expire in 1 year

            # Create the downloadable file
            file_obj = DownloadableFile.objects.create(
                title=file_data['title'],
                description=file_data['description'],
                file=uploaded_file,
                category=file_data['category'],
                priority=file_data['priority'],
                is_featured=file_data['is_featured'],
                requires_login=file_data['requires_login'],
                tags=file_data['tags'],
                expires_at=expires_at
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created: {file_obj.title} ({file_obj.get_category_display()})')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} sample downloadable files!')
        )
        
        # Display summary
        self.stdout.write('\nSummary:')
        for category_code, category_name in FileCategory.choices:
            count = DownloadableFile.objects.filter(category=category_code).count()
            self.stdout.write(f'  {category_name}: {count} files')
        
        featured_count = DownloadableFile.objects.filter(is_featured=True).count()
        urgent_count = DownloadableFile.objects.filter(priority=PriorityLevel.URGENT).count()
        login_required_count = DownloadableFile.objects.filter(requires_login=True).count()
        
        self.stdout.write(f'\nFeatured files: {featured_count}')
        self.stdout.write(f'Urgent priority files: {urgent_count}')
        self.stdout.write(f'Login required files: {login_required_count}')
