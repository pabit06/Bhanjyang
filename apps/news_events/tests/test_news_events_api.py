from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.news_events.models import NewsArticle, Event, Category
from django.contrib.auth import get_user_model

User = get_user_model()

class NewsEventsAPIViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        
        self.article = NewsArticle.objects.create(
            title='Test Article',
            content='Test Content',
            category=self.category,
            author=self.user,
            status=NewsArticle.Status.PUBLISHED,
            published_date=timezone.now()
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            event_date=timezone.now() + timezone.timedelta(days=1),
            status=Event.Status.PUBLISHED
        )

    def test_get_articles(self):
        url = reverse('news_events:content_api', kwargs={'content_type': 'articles'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Test Article')

    def test_get_events(self):
        url = reverse('news_events:content_api', kwargs={'content_type': 'events'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Test Event')

    def test_invalid_content_type(self):
        url = reverse('news_events:content_api', kwargs={'content_type': 'invalid'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
