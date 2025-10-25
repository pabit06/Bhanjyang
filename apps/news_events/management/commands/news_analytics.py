# news_events/management/commands/news_analytics.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Sum
from apps.news_events.models import NewsArticle, Event, Category, Subscriber, Comment, ContentAnalytics
from apps.news_events.performance import NewsEventsQueryOptimizer

class Command(BaseCommand):
    help = 'Generate comprehensive news and events analytics report'

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
        file_path = options.get('file')
        
        self.stdout.write(f"Generating news analytics for the last {days} days...")
        
        # Generate analytics data
        analytics_data = self.generate_analytics(days)
        
        # Output based on format
        if output_format == 'console':
            self.output_to_console(analytics_data)
        elif output_format == 'file':
            if not file_path:
                self.stderr.write("File path is required when output format is 'file'")
                return
            self.output_to_file(analytics_data, file_path)
        elif output_format == 'json':
            self.output_to_json(analytics_data)
        
        self.stdout.write(self.style.SUCCESS("Analytics report generated successfully"))

    def generate_analytics(self, days):
        """Generate comprehensive analytics data"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Basic statistics
        basic_stats = NewsEventsQueryOptimizer.get_article_statistics()
        event_stats = NewsEventsQueryOptimizer.get_event_statistics()
        
        # Category breakdown
        category_stats = NewsEventsQueryOptimizer.get_category_statistics()
        
        # Popular content
        popular_articles = NewsEventsQueryOptimizer.get_popular_articles(limit=10)
        upcoming_events = NewsEventsQueryOptimizer.get_upcoming_events(limit=10)
        
        # Content trends
        trends = NewsEventsQueryOptimizer.get_content_trends(days)
        
        # User engagement
        engagement = NewsEventsQueryOptimizer.get_user_engagement_patterns()
        
        # Subscriber statistics
        subscriber_stats = self.get_subscriber_statistics()
        
        # Comment statistics
        comment_stats = self.get_comment_statistics(start_date, end_date)
        
        return {
            'period': f"{days} days",
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'basic_stats': basic_stats,
            'event_stats': event_stats,
            'category_stats': category_stats,
            'popular_articles': popular_articles,
            'upcoming_events': upcoming_events,
            'trends': trends,
            'engagement': engagement,
            'subscriber_stats': subscriber_stats,
            'comment_stats': comment_stats,
        }

    def get_subscriber_statistics(self):
        """Get subscriber statistics"""
        total_subscribers = Subscriber.objects.count()
        active_subscribers = Subscriber.objects.filter(status=Subscriber.Status.ACTIVE).count()
        confirmed_subscribers = Subscriber.objects.filter(is_confirmed=True).count()
        
        # Recent subscriptions
        recent_subscriptions = Subscriber.objects.filter(
            subscribed_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Engagement metrics
        avg_opens = Subscriber.objects.aggregate(avg_opens=Avg('open_count'))['avg_opens'] or 0
        avg_clicks = Subscriber.objects.aggregate(avg_clicks=Avg('click_count'))['avg_clicks'] or 0
        
        return {
            'total_subscribers': total_subscribers,
            'active_subscribers': active_subscribers,
            'confirmed_subscribers': confirmed_subscribers,
            'recent_subscriptions': recent_subscriptions,
            'avg_opens': round(avg_opens, 2),
            'avg_clicks': round(avg_clicks, 2),
        }

    def get_comment_statistics(self, start_date, end_date):
        """Get comment statistics"""
        total_comments = Comment.objects.count()
        approved_comments = Comment.objects.filter(status=Comment.Status.APPROVED).count()
        pending_comments = Comment.objects.filter(status=Comment.Status.PENDING).count()
        spam_comments = Comment.objects.filter(status=Comment.Status.SPAM).count()
        
        # Recent comments
        recent_comments = Comment.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        # Average likes
        avg_likes = Comment.objects.aggregate(avg_likes=Avg('like_count'))['avg_likes'] or 0
        
        return {
            'total_comments': total_comments,
            'approved_comments': approved_comments,
            'pending_comments': pending_comments,
            'spam_comments': spam_comments,
            'recent_comments': recent_comments,
            'avg_likes': round(avg_likes, 2),
        }

    def output_to_console(self, data):
        """Output analytics to console"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("NEWS & EVENTS ANALYTICS REPORT")
        self.stdout.write("="*60)
        
        # Basic statistics
        self.stdout.write(f"\nPERIOD: {data['period']} ({data['start_date']} to {data['end_date']})")
        self.stdout.write("\nBASIC STATISTICS")
        self.stdout.write("-" * 40)
        
        basic_stats = data['basic_stats']
        self.stdout.write(f"Total Articles: {basic_stats.get('total_articles', 0)}")
        self.stdout.write(f"Published Articles: {basic_stats.get('published_articles', 0)}")
        self.stdout.write(f"Draft Articles: {basic_stats.get('draft_articles', 0)}")
        self.stdout.write(f"Featured Articles: {basic_stats.get('featured_articles', 0)}")
        self.stdout.write(f"Total Views: {basic_stats.get('total_views', 0)}")
        self.stdout.write(f"Total Shares: {basic_stats.get('total_shares', 0)}")
        avg_read_time = basic_stats.get('avg_read_time', 0) or 0
        self.stdout.write(f"Average Read Time: {avg_read_time:.1f} minutes")
        
        # Event statistics
        event_stats = data['event_stats']
        self.stdout.write(f"\nEVENT STATISTICS")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Total Events: {event_stats.get('total_events', 0)}")
        self.stdout.write(f"Upcoming Events: {event_stats.get('upcoming_events', 0)}")
        self.stdout.write(f"Past Events: {event_stats.get('past_events', 0)}")
        self.stdout.write(f"Featured Events: {event_stats.get('featured_events', 0)}")
        self.stdout.write(f"Total Event Views: {event_stats.get('total_views', 0)}")
        
        # Category breakdown
        self.stdout.write(f"\nCATEGORY BREAKDOWN")
        self.stdout.write("-" * 40)
        for category in data['category_stats']:
            self.stdout.write(f"{category.name}: {category.article_count} articles")
        
        # Popular articles
        self.stdout.write(f"\nTOP 5 POPULAR ARTICLES")
        self.stdout.write("-" * 40)
        for i, article in enumerate(data['popular_articles'][:5], 1):
            self.stdout.write(f"{i}. {article.title} ({article.view_count} views)")
        
        # Upcoming events
        self.stdout.write(f"\nUPCOMING EVENTS")
        self.stdout.write("-" * 40)
        for event in data['upcoming_events'][:5]:
            self.stdout.write(f"- {event.title} ({event.event_date.strftime('%Y-%m-%d')})")
        
        # Subscriber statistics
        subscriber_stats = data['subscriber_stats']
        self.stdout.write(f"\nSUBSCRIBER STATISTICS")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Total Subscribers: {subscriber_stats['total_subscribers']}")
        self.stdout.write(f"Active Subscribers: {subscriber_stats['active_subscribers']}")
        self.stdout.write(f"Confirmed Subscribers: {subscriber_stats['confirmed_subscribers']}")
        self.stdout.write(f"Recent Subscriptions (7 days): {subscriber_stats['recent_subscriptions']}")
        self.stdout.write(f"Average Opens: {subscriber_stats['avg_opens']}")
        self.stdout.write(f"Average Clicks: {subscriber_stats['avg_clicks']}")
        
        # Comment statistics
        comment_stats = data['comment_stats']
        self.stdout.write(f"\nCOMMENT STATISTICS")
        self.stdout.write("-" * 40)
        self.stdout.write(f"Total Comments: {comment_stats['total_comments']}")
        self.stdout.write(f"Approved Comments: {comment_stats['approved_comments']}")
        self.stdout.write(f"Pending Comments: {comment_stats['pending_comments']}")
        self.stdout.write(f"Spam Comments: {comment_stats['spam_comments']}")
        self.stdout.write(f"Recent Comments: {comment_stats['recent_comments']}")
        self.stdout.write(f"Average Likes: {comment_stats['avg_likes']}")

    def output_to_file(self, data, file_path):
        """Output analytics to file"""
        import json
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        self.stdout.write(f"Analytics report saved to {file_path}")

    def output_to_json(self, data):
        """Output analytics as JSON"""
        import json
        
        json_output = json.dumps(data, indent=2, default=str, ensure_ascii=False)
        self.stdout.write(json_output)
