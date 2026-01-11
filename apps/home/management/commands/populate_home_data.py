"""
Django management command to populate home app with sample data.
Usage: python manage.py populate_home_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.home.models import (
    HomePageContent, Testimonial, Statistic, Announcement,
    NewsletterSubscriber
)


class Command(BaseCommand):
    help = 'Populate home app with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            HomePageContent.objects.all().delete()
            Testimonial.objects.all().delete()
            Statistic.objects.all().delete()
            Announcement.objects.all().delete()

            NewsletterSubscriber.objects.all().delete()

        self.stdout.write('Creating sample data for home app...')

        # Create homepage content
        self.create_homepage_content()
        
        # Create testimonials
        self.create_testimonials()
        
        # Create statistics
        self.create_statistics()
        
        # Create announcements
        self.create_announcements()
        

        
        # Create newsletter subscribers
        self.create_newsletter_subscribers()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated home app with sample data!')
        )

    def create_homepage_content(self):
        """Create homepage content"""
        content, created = HomePageContent.objects.get_or_create(
            title="Empowering Your Financial Journey in Rupa",
            defaults={
                'subtitle': "Bhanjyang Cooperative - Your Trusted Financial Partner",
                'description': "भञ्ज्याङ बचत तथा ऋण सहकारी संस्था लिमिटेड - तपाईंको विश्वासिलो वित्तीय साझेदार। बचत खाता, ऋण सेवा, र अन्य वित्तीय सेवाहरू।",
                'is_active': True,
                'order': 1,
                'meta_title': "Bhanjyang Cooperative - Home",
                'meta_description': "भञ्ज्याङ बचत तथा ऋण सहकारी संस्था लिमिटेडको मुख्य पृष्ठ। हामीले बचत खाता, ऋण सेवा, र अन्य वित्तीय सेवाहरू प्रदान गर्छौं।",
                'meta_keywords': "bhanjyang cooperative, savings account, credit services, financial services nepal, kaski cooperative, rupa banking, microfinance nepal"
            }
        )
        
        if created:
            self.stdout.write(f'Created homepage content: {content.title}')

    def create_testimonials(self):
        """Create sample testimonials"""
        testimonials_data = [
            {
                'name': 'Tek Bahadur Gurung',
                'position': 'Community Member',
                'company': 'Local Farmer',
                'content': 'The savings accounts offered by Bhanjyang Cooperative are excellent. I feel secure knowing my hard-earned money is growing safely with them.',
                'rating': 5,
                'language': 'en',
                'is_featured': True,
                'order': 1
            },
            {
                'name': 'Prajjwol Sharma',
                'position': 'Farmer & Member',
                'company': 'Agricultural Cooperative',
                'content': 'Their team is incredibly supportive and always ready to help. Bhanjyang Cooperative is more than a bank; it\'s a partner in our progress.',
                'rating': 5,
                'language': 'en',
                'is_featured': True,
                'order': 2
            },
            {
                'name': 'Sita Devi',
                'position': 'Small Business Owner',
                'company': 'Local Shop',
                'content': 'The loan services helped me expand my business. The interest rates are fair and the process is transparent.',
                'rating': 4,
                'language': 'en',
                'is_featured': True,
                'order': 3
            },
            {
                'name': 'राम बहादुर गुरुङ',
                'position': 'सदस्य',
                'company': 'स्थानीय किसान',
                'content': 'भञ्ज्याङ सहकारीको सेवा धेरै राम्रो छ। हाम्रो पैसा सुरक्षित रहेको देखेर मन शान्त छ।',
                'rating': 5,
                'language': 'ne',
                'is_featured': False,
                'order': 4
            }
        ]

        for data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created testimonial: {testimonial.name}')

    def create_statistics(self):
        """Create sample statistics"""
        statistics_data = [
            {
                'title': 'Total Members',
                'value': '2,500+',
                'description': 'Active cooperative members',
                'icon': 'fas fa-users',
                'color': 'green',
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'Total Savings',
                'value': 'Rs. 50M+',
                'description': 'Member savings deposits',
                'icon': 'fas fa-piggy-bank',
                'color': 'blue',
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'Loans Disbursed',
                'value': 'Rs. 30M+',
                'description': 'Total loans provided',
                'icon': 'fas fa-hand-holding-usd',
                'color': 'purple',
                'is_featured': True,
                'order': 3
            },
            {
                'title': 'Years of Service',
                'value': '25+',
                'description': 'Serving the community',
                'icon': 'fas fa-calendar-alt',
                'color': 'red',
                'is_featured': True,
                'order': 4
            }
        ]

        for data in statistics_data:
            statistic, created = Statistic.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created statistic: {statistic.title}')

    def create_announcements(self):
        """Create sample announcements"""
        announcements_data = [
            {
                'title': 'New Interest Rates Effective from Next Month',
                'summary': 'We are pleased to announce new competitive interest rates for our savings accounts.',
                'content': 'Dear Members, We are pleased to announce that starting next month, we will be offering new competitive interest rates for our various savings accounts. Regular savings accounts will earn up to 8% annually, while fixed deposits will earn up to 7% for terms of 1 year or more.',
                'announcement_type': 'service',
                'priority': 'high',
                'is_featured': True,
                'publish_date': timezone.now()
            },
            {
                'title': 'Annual General Meeting 2025',
                'summary': 'Save the date for our upcoming Annual General Meeting.',
                'content': 'All members are invited to attend our Annual General Meeting scheduled for March 15, 2025. The meeting will be held at our main office in Rupa Rural Municipality. Important decisions regarding cooperative policies and financial reports will be discussed.',
                'announcement_type': 'event',
                'priority': 'medium',
                'is_featured': True,
                'publish_date': timezone.now()
            },
            {
                'title': 'Holiday Notice - Dashain Festival',
                'summary': 'Office will be closed during Dashain festival.',
                'content': 'Our office will be closed from October 10-15, 2025, for Dashain festival celebrations. We will resume normal operations on October 16, 2025. We wish all our members a happy and prosperous Dashain!',
                'announcement_type': 'holiday',
                'priority': 'medium',
                'is_featured': False,
                'publish_date': timezone.now()
            }
        ]

        for data in announcements_data:
            announcement, created = Announcement.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created announcement: {announcement.title}')





    def create_newsletter_subscribers(self):
        """Create sample newsletter subscribers"""
        subscribers_data = [
            {'email': 'member1@example.com', 'name': 'John Doe'},
            {'email': 'member2@example.com', 'name': 'Jane Smith'},
            {'email': 'member3@example.com', 'name': 'Ram Bahadur'},
        ]

        for data in subscribers_data:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created newsletter subscriber: {subscriber.email}')
