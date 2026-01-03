"""
Management command to fix empty slugs for NewsArticle, Event, and Category models.
This is useful when titles contain Nepali or other Unicode characters that weren't
properly slugified before.
"""

from django.core.management.base import BaseCommand
from apps.news_events.models import NewsArticle, Event, Category, slugify_nepali


class Command(BaseCommand):
    help = 'Fix empty slugs for NewsArticle, Event, and Category models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without actually fixing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Fix NewsArticle slugs
        articles = NewsArticle.objects.filter(slug='')
        article_count = articles.count()
        if article_count > 0:
            self.stdout.write(f'\nFound {article_count} articles with empty slugs')
            fixed = 0
            for article in articles:
                new_slug = slugify_nepali(article.title)
                if new_slug:
                    # Check for uniqueness
                    original_slug = new_slug
                    counter = 1
                    while NewsArticle.objects.filter(slug=new_slug).exclude(pk=article.pk).exists():
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    if not dry_run:
                        article.slug = new_slug
                        article.save(update_fields=['slug'])
                    # Use ASCII-safe output for Windows console
                    try:
                        title_preview = article.title[:50]
                    except UnicodeEncodeError:
                        title_preview = f"Article ID: {article.id}"
                    self.stdout.write(
                        f'  Article "{title_preview}..." -> slug: {new_slug}'
                    )
                    fixed += 1
                else:
                    try:
                        title_preview = article.title[:50]
                    except UnicodeEncodeError:
                        title_preview = f"Article ID: {article.id}"
                    self.stdout.write(
                        self.style.ERROR(f'  Could not generate slug for article: {title_preview}...')
                    )
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} article slugs'))
        else:
            self.stdout.write(self.style.SUCCESS('No articles with empty slugs found'))
        
        # Fix Event slugs
        events = Event.objects.filter(slug='')
        event_count = events.count()
        if event_count > 0:
            self.stdout.write(f'\nFound {event_count} events with empty slugs')
            fixed = 0
            for event in events:
                new_slug = slugify_nepali(event.title)
                if new_slug:
                    # Check for uniqueness
                    original_slug = new_slug
                    counter = 1
                    while Event.objects.filter(slug=new_slug).exclude(pk=event.pk).exists():
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    if not dry_run:
                        event.slug = new_slug
                        event.save(update_fields=['slug'])
                    # Use ASCII-safe output for Windows console
                    try:
                        title_preview = event.title[:50]
                    except UnicodeEncodeError:
                        title_preview = f"Event ID: {event.id}"
                    self.stdout.write(
                        f'  Event "{title_preview}..." -> slug: {new_slug}'
                    )
                    fixed += 1
                else:
                    try:
                        title_preview = event.title[:50]
                    except UnicodeEncodeError:
                        title_preview = f"Event ID: {event.id}"
                    self.stdout.write(
                        self.style.ERROR(f'  Could not generate slug for event: {title_preview}...')
                    )
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} event slugs'))
        else:
            self.stdout.write(self.style.SUCCESS('No events with empty slugs found'))
        
        # Fix Category slugs
        categories = Category.objects.filter(slug='')
        category_count = categories.count()
        if category_count > 0:
            self.stdout.write(f'\nFound {category_count} categories with empty slugs')
            fixed = 0
            for category in categories:
                new_slug = slugify_nepali(category.name)
                if new_slug:
                    # Check for uniqueness
                    original_slug = new_slug
                    counter = 1
                    while Category.objects.filter(slug=new_slug).exclude(pk=category.pk).exists():
                        new_slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    if not dry_run:
                        category.slug = new_slug
                        category.save(update_fields=['slug'])
                    # Use ASCII-safe output for Windows console
                    try:
                        name_preview = category.name[:50]
                    except UnicodeEncodeError:
                        name_preview = f"Category ID: {category.id}"
                    self.stdout.write(
                        f'  Category "{name_preview}..." -> slug: {new_slug}'
                    )
                    fixed += 1
                else:
                    try:
                        name_preview = category.name[:50]
                    except UnicodeEncodeError:
                        name_preview = f"Category ID: {category.id}"
                    self.stdout.write(
                        self.style.ERROR(f'  Could not generate slug for category: {name_preview}...')
                    )
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} category slugs'))
        else:
            self.stdout.write(self.style.SUCCESS('No categories with empty slugs found'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN COMPLETE - No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS('\nAll empty slugs have been fixed!'))

