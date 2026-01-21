# downloads/management/commands/create_sample_downloads.py

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.downloads.models import DownloadableFile, FileCategory, PriorityLevel

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample downloadable files with different priorities and categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new ones',
        )
        parser.add_argument(
            '--from-folder',
            type=str,
            default=None,
            help='Path to folder containing files to seed (e.g., E:\\Resource\\Downloads for Website)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating files',
        )

    def handle(self, *args, **options):
        # If --from-folder is provided, seed from folder
        if options.get('from_folder'):
            self._seed_from_folder(options)
            return
        
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
    
    def _seed_from_folder(self, options):
        """Seed files from a folder."""
        folder_path = Path(options['from_folder'])
        
        if not folder_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Folder not found: {folder_path}')
            )
            return
        
        if options['clear']:
            if not options['dry_run']:
                self.stdout.write('Clearing existing files...')
                DownloadableFile.objects.all().delete()
            else:
                self.stdout.write('Would clear existing files...')
        
        # File mapping based on filename patterns
        file_mappings = {
            'KYM-Form.pdf': {
                'title': 'Know Your Member (KYM) Form',
                'description': 'Know Your Member form for member verification and KYC compliance.',
                'category': FileCategory.FORM,
                'priority': PriorityLevel.HIGH,
                'is_featured': True,
                'requires_login': False,
                'tags': 'KYM, KYC, member verification, form',
            },
            'Membership-Application-form.pdf': {
                'title': 'Membership Application Form',
                'description': 'Complete membership application form for new members. Please fill out all required fields.',
                'category': FileCategory.FORM,
                'priority': PriorityLevel.HIGH,
                'is_featured': True,
                'requires_login': False,
                'tags': 'membership, application, form, new member',
            },
            'ATM-Card-Application-form.pdf': {
                'title': 'ATM Card Application Form',
                'description': 'Application form for ATM card services. Includes terms and conditions.',
                'category': FileCategory.FORM,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': True,
                'requires_login': False,
                'tags': 'ATM, card, application, banking, form',
            },
            'Mobile-Banking-Aplication-form.pdf': {
                'title': 'Mobile Banking Application Form',
                'description': 'Application form for mobile banking services. Enable banking on your mobile device.',
                'category': FileCategory.FORM,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': True,
                'requires_login': False,
                'tags': 'mobile banking, application, form, digital banking',
            },
            'Election-Policy-Updated-2080.pdf': {
                'title': 'Election Policy (Updated 2080)',
                'description': 'Updated election policy and procedures for cooperative board elections.',
                'category': FileCategory.POLICY,
                'priority': PriorityLevel.HIGH,
                'is_featured': True,
                'requires_login': False,
                'tags': 'election, policy, governance, board, 2080',
            },
            'Management-report-format_NCBL.pdf': {
                'title': 'Management Report Format (NCBL)',
                'description': 'Standard management report format as per NCBL guidelines for cooperatives.',
                'category': FileCategory.REPORT,
                'priority': PriorityLevel.MEDIUM,
                'is_featured': False,
                'requires_login': True,
                'tags': 'management, report, format, NCBL, template',
            },
            'Model NFRS for SMEs Financial Statement _Cooperative_English-Final.pdf': {
                'title': 'Model NFRS for SMEs Financial Statement - Cooperative (English)',
                'description': 'Model financial statement format for cooperatives as per NFRS for SMEs guidelines.',
                'category': FileCategory.REPORT,
                'priority': PriorityLevel.HIGH,
                'is_featured': True,
                'requires_login': True,
                'tags': 'NFRS, financial statement, model, cooperative, SMEs, template',
            },
        }
        
        allowed_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            default_user = User.objects.filter(is_staff=True).first()
            if not default_user:
                default_user = User.objects.first()
        except:
            default_user = None
        
        self.stdout.write(f'Scanning folder: {folder_path}')
        self.stdout.write('')
        
        for file_path in folder_path.iterdir():
            if not file_path.is_file():
                continue
            
            file_ext = file_path.suffix.lower()
            if file_ext not in allowed_extensions:
                skipped_count += 1
                continue
            
            # Skip image files
            name_lower = file_path.name.lower()
            if name_lower.startswith(('hero-', 'download-hero', 'plant-', 'election_policy_thumbnail', 'mobile_banking_form_thumbnail')) or file_ext in {'.jpg', '.jpeg', '.png'}:
                skipped_count += 1
                continue
            
            file_name = file_path.name
            file_metadata = file_mappings.get(file_name, {})
            
            title = file_metadata.get('title', file_path.stem.replace('_', ' ').replace('-', ' ').title())
            description = file_metadata.get('description', f'{title} - Available for download.')
            category = file_metadata.get('category', FileCategory.OTHER)
            priority = file_metadata.get('priority', PriorityLevel.MEDIUM)
            is_featured = file_metadata.get('is_featured', False)
            requires_login = file_metadata.get('requires_login', False)
            tags = file_metadata.get('tags', '')
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.SUCCESS(f'Would create: {title} ({category})')
                )
                created_count += 1
                continue
            
            try:
                if DownloadableFile.objects.filter(title=title).exists():
                    skipped_count += 1
                    if options.get('verbosity', 1) >= 2:
                        self.stdout.write(
                            self.style.WARNING(f'Already exists: {title}')
                        )
                    continue
                
                with open(file_path, 'rb') as f:
                    django_file = File(f, name=file_path.name)
                    file_obj = DownloadableFile.objects.create(
                        title=title,
                        description=description,
                        file=django_file,
                        category=category,
                        priority=priority,
                        is_featured=is_featured,
                        requires_login=requires_login,
                        tags=tags,
                        uploaded_by=default_user,
                    )
                    created_count += 1
                    # Use ASCII-safe output
                    category_display = str(file_obj.get_category_display())
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {title} ({category_display})')
                    )
            except Exception as e:
                error_count += 1
                error_msg = str(e).encode('ascii', 'replace').decode('ascii')
                self.stdout.write(
                    self.style.ERROR(f'Error creating {file_path.name}: {error_msg}')
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        if options['dry_run']:
            self.stdout.write(self.style.SUCCESS(f'DRY RUN - Would create: {created_count} files'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created: {created_count} files'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} files'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count} files'))
