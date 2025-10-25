from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from apps.news_events.models import Category, NewsArticle, Event, Subscriber, Comment


class Command(BaseCommand):
    help = "Seed demo data for news_events (categories, articles, events, comments, subscribers)"

    def add_arguments(self, parser):
        parser.add_argument('--articles', type=int, default=8, help='Number of articles to create')
        parser.add_argument('--events', type=int, default=5, help='Number of events to create')

    @transaction.atomic
    def handle(self, *args, **options):
        articles_count = options['articles']
        events_count = options['events']

        self.stdout.write(self.style.NOTICE('Seeding news_events demo data...'))

        # Ensure an author exists
        author, _ = User.objects.get_or_create(
            username='demo_author',
            defaults={'first_name': 'Demo', 'last_name': 'Author', 'email': 'demo@author.test'}
        )

        # Categories
        categories_spec = [
            ("General", "general", "General updates and announcements", "#059669", "fas fa-bullhorn"),
            ("Finance", "finance", "Financial news and reports", "#2563eb", "fas fa-coins"),
            ("Community", "community", "Community programs and events", "#dc2626", "fas fa-users"),
            ("Training", "training", "Workshops and training", "#7c3aed", "fas fa-chalkboard-teacher"),
        ]
        categories = []
        for name, slug, desc, color, icon in categories_spec:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'color': color,
                    'icon': icon,
                    'is_active': True,
                    'sort_order': len(categories),
                }
            )
            categories.append(cat)

        # Articles
        created_articles = []
        for i in range(articles_count):
            category = categories[i % len(categories)]
            title = f"Demo Article {i+1}: {category.name} Insights"
            article, _ = NewsArticle.objects.get_or_create(
                slug=f"demo-article-{i+1}",
                defaults={
                    'title': title,
                    'category': category,
                    'author': author,
                    'content': (
                        "<p>This is demo content for the news article. It demonstrates the layout, "
                        "styling, and features like read time, views, and sharing.</p>"
                    ),
                    'excerpt': "This is a short summary of the demo article.",
                    'status': NewsArticle.Status.PUBLISHED,
                    'priority': NewsArticle.Priority.MEDIUM,
                    'published_date': timezone.now() - timezone.timedelta(days=(i % 7)),
                    'is_featured': (i % 4 == 0),
                    'allow_comments': True,
                }
            )
            created_articles.append(article)

        # Comments on first two articles
        for idx, article in enumerate(created_articles[:2], start=1):
            Comment.objects.get_or_create(
                article=article,
                author_name=f"Visitor {idx}",
                author_email=f"visitor{idx}@example.com",
                defaults={
                    'content': "Great article! Thanks for sharing.",
                    'is_approved': True,
                    'status': Comment.Status.APPROVED,
                }
            )

        # Events
        created_events = []
        now = timezone.now()
        for i in range(events_count):
            title = f"Community Event {i+1}"
            event, _ = Event.objects.get_or_create(
                slug=f"community-event-{i+1}",
                defaults={
                    'title': title,
                    'description': "Join us for a cooperative community engagement session.",
                    'short_description': "A short description of the event.",
                    'event_type': Event.EventType.MEETING if i % 2 == 0 else Event.EventType.WORKSHOP,
                    'location': "Main Hall",
                    'address': "Bhanjyang Cooperative, Central Office",
                    'event_date': now + timezone.timedelta(days=(i + 1)),
                    'end_date': now + timezone.timedelta(days=(i + 1), hours=2),
                    'status': Event.Status.PUBLISHED,
                    'is_featured': (i % 3 == 0),
                    'registration_required': (i % 2 == 0),
                }
            )
            created_events.append(event)

        # Subscribers
        for i in range(3):
            Subscriber.objects.get_or_create(
                email=f"subscriber{i+1}@example.com",
                defaults={'is_confirmed': True, 'status': Subscriber.Status.ACTIVE}
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {len(categories)} categories, {len(created_articles)} articles, {len(created_events)} events, 3 subscribers."
        ))


