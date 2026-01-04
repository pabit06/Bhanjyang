from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.about.models import CooperativeInfo, CooperativeTimeline, CooperativeStatistic, CooperativeAffiliation, LeadershipMessage

class Command(BaseCommand):
    help = 'Populate the database with initial About Us data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting population of about data...'))
        
        # Create company information
        CooperativeInfo.objects.all().delete() # Clear existing
        company_info = CooperativeInfo.objects.create(
            cooperative_name="Bhanjyang Saving & Credit Cooperative Society Ltd.",
            cooperative_name_nepali="भञ्ज्याङ्ग बचत तथा ऋण सहकारी संस्था लिमिटेड",
            established_date=timezone.now().date().replace(year=2010, month=4, day=15),
            registration_number="REG-2010-001",
            license_number="LIC-2010-001",
            address="Rupa Rural Municipality, Kaski, Nepal",
            phone="+977-61-XXXXXXX",
            email="info@bhanjyang.coop.np",
            website="https://bhanjyang.coop.np",
            mission="To provide accessible and fair financial solutions to uplift local communities in Rupa Rural Municipality, fostering economic growth and community development.",
            vision="To be the most trusted and preferred financial partner for community development in our region.",
            values="Integrity, Transparency, Community Focus, Financial Inclusion, Sustainable Growth, Member Empowerment",
            description="Bhanjyang Saving & Credit Cooperative Society Ltd. is dedicated to fostering economic growth and community development through reliable financial services in Rupa Rural Municipality, Kaski. We believe in strengthening the local economy by empowering individuals and businesses through savings, credit, and expert financial guidance.",
            description_nepali="भञ्ज्याङ्ग बचत तथा ऋण सहकारी संस्था लिमिटेड रुपा गाउँपालिका, कास्कीमा विश्वसनीय वित्तीय सेवाहरू मार्फत आर्थिक वृद्धि र समुदाय विकासलाई बढावा दिन समर्पित छ।",
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created company info: {company_info.cooperative_name}'))
        
        # Create sample timeline events
        timeline_events = [
            {
                'title': 'Cooperative Established',
                'description': 'Bhanjyang Saving & Credit Cooperative Society Ltd. was officially established with a vision to serve the local community.',
                'event_date': timezone.now().date().replace(year=2010, month=4, day=15),
                'event_type': 'milestone'
            },
            {
                'title': 'First Branch Opening',
                'description': 'Opened our first branch office in Rupa Rural Municipality to better serve our members.',
                'event_date': timezone.now().date().replace(year=2012, month=6, day=1),
                'event_type': 'expansion'
            },
            {
                'title': '1000 Members Milestone',
                'description': 'Reached our first major milestone of 1000 active members.',
                'event_date': timezone.now().date().replace(year=2015, month=3, day=10),
                'event_type': 'achievement'
            },
            {
                'title': 'Digital Services Launch',
                'description': 'Launched online banking and digital services for our members.',
                'event_date': timezone.now().date().replace(year=2022, month=8, day=15),
                'event_type': 'milestone'
            }
        ]
        
        for event_data in timeline_events:
            event = CooperativeTimeline.objects.create(
                title=event_data['title'],
                description=event_data['description'],
                event_date=event_data['event_date'],
                event_type=event_data['event_type'],
                is_featured=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created timeline event: {event.title}'))
        
        # Removed: Achievements creation - CooperativeAchievement model no longer exists
        
        # Create sample statistics
        statistics = [
            {
                'title': 'Total Members',
                'value': '2,500',
                'unit': 'Members',
                'statistic_type': 'members',
                'icon': 'fas fa-users',
                'color': 'deuraligreen'
            },
            {
                'title': 'Total Deposits',
                'value': '50',
                'unit': 'Million NPR',
                'statistic_type': 'deposits',
                'icon': 'fas fa-piggy-bank',
                'color': 'bhanjyangred'
            },
            {
                'title': 'Loans Disbursed',
                'value': '30',
                'unit': 'Million NPR',
                'statistic_type': 'loans',
                'icon': 'fas fa-hand-holding-usd',
                'color': 'deuraligreen'
            },
            {
                'title': 'Service Branches',
                'value': '3',
                'unit': 'Branches',
                'statistic_type': 'branches',
                'icon': 'fas fa-building',
                'color': 'bhanjyangred'
            }
        ]
        
        for stat_data in statistics:
            stat = CooperativeStatistic.objects.create(
                title=stat_data['title'],
                value=stat_data['value'],
                unit=stat_data['unit'],
                statistic_type=stat_data['statistic_type'],
                icon=stat_data['icon'],
                color=stat_data['color'],
                is_featured=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created statistic: {stat.title}'))
        
        # Create sample affiliations
        affiliations = [
            {
                'name': 'NEFSCUN',
                'description': 'Nepal Federation of Savings and Credit Cooperative Unions',
                'affiliation_type': 'association',
                'website': 'https://nefscun.org.np'
            },
            {
                'name': 'Kaski District Cooperative Association',
                'description': 'Local cooperative association for Kaski district',
                'affiliation_type': 'association',
                'website': ''
            },
            {
                'name': 'Cooperative Development Board',
                'description': 'Government regulatory body for cooperatives',
                'affiliation_type': 'regulatory',
                'website': ''
            }
        ]
        
        for affiliation_data in affiliations:
            affiliation = CooperativeAffiliation.objects.create(
                name=affiliation_data['name'],
                description=affiliation_data['description'],
                affiliation_type=affiliation_data['affiliation_type'],
                website=affiliation_data['website'],
                is_featured=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created affiliation: {affiliation.name}'))
        
        # Create sample leadership messages
        leadership_messages = [
            {
                'title': 'Message from Chairman',
                'message_type': 'chairman',
                'content': 'As Chairman of Bhanjyang Cooperative, I am proud of our journey in serving the community. We remain committed to providing accessible financial services and fostering community development.',
                'author_name': 'Ram Bahadur Thapa', 
                'author_position': 'Chairman'
            },
            {
                'title': 'Message from Manager',
                'message_type': 'manager',
                'content': 'Our team is dedicated to ensuring the highest standards of service for our members. We continuously work to improve our services and expand our reach in the community.',
                'author_name': 'Sita Devi Sharma', 
                'author_position': 'Manager'
            }
        ]
        
        for message_data in leadership_messages:
            message = LeadershipMessage.objects.create(
                title=message_data['title'],
                message_type=message_data['message_type'],
                content=message_data['content'],
                author_name=message_data['author_name'],
                author_position=message_data['author_position'],
                is_featured=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created leadership message: {message.title}'))
        
        self.stdout.write(self.style.SUCCESS('About data populated successfully!'))
