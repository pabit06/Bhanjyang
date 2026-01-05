"""
Load Testing and Performance Tests for News Events App

These tests simulate high load scenarios with multiple concurrent users
to verify system performance under stress.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, TransactionTestCase, override_settings
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from unittest.mock import patch

from apps.news_events.models import (
    Category, NewsArticle, Event, Subscriber, Comment
)
from apps.news_events.services import NewsService, EventService
from apps.news_events.performance import NewsEventsCache

User = get_user_model()


class LoadTestBase(TransactionTestCase):
    """
    Base class for load tests with setup for concurrent testing.
    """
    
    def setUp(self):
        """Set up test data for load testing."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='loadtestuser',
            email='loadtest@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Load Test Category',
            slug='load-test',
            is_active=True
        )
        
        # Create multiple articles for load testing
        self.articles = []
        for i in range(50):
            article = NewsArticle.objects.create(
                title=f'Load Test Article {i}',
                slug=f'load-test-article-{i}',
                category=self.category,
                author=self.user,
                content=f'Content for load test article {i}. ' * 10,  # Longer content
                excerpt=f'Excerpt {i}',
                status=NewsArticle.Status.PUBLISHED,
                published_date=timezone.now() - timedelta(days=i % 30),
                is_featured=(i < 10)
            )
            self.articles.append(article)
        
        # Create multiple events
        self.events = []
        for i in range(20):
            event = Event.objects.create(
                title=f'Load Test Event {i}',
                slug=f'load-test-event-{i}',
                description=f'Description for load test event {i}',
                event_type=Event.EventType.MEETING,
                status=Event.Status.PUBLISHED,
                event_date=timezone.now() + timedelta(days=i+1),
                is_featured=(i < 5)
            )
            self.events.append(event)
        
        # Clear cache before tests
        cache.clear()


class ConcurrentRequestLoadTest(LoadTestBase):
    """
    Test system performance under concurrent request load.
    """
    
    def test_concurrent_home_page_requests(self):
        """
        Test home page performance with 50 concurrent requests.
        Target: All requests complete in < 2 seconds.
        """
        num_requests = 50
        url = reverse('news_events:home')
        results = []
        
        def make_request(request_id):
            """Make a single request and return timing."""
            start_time = time.time()
            try:
                client = Client()
                response = client.get(url)
                end_time = time.time()
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'status': 0,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        max_time = max(r['time'] for r in successful) if successful else 0
        min_time = min(r['time'] for r in successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_requests * 0.95,  # 95% success rate
                               f"Only {len(successful)}/{num_requests} requests succeeded")
        self.assertLess(avg_time, 2.0,  # Average response time < 2 seconds
                       f"Average response time {avg_time:.2f}s exceeds 2s")
        self.assertLess(max_time, 5.0,  # Max response time < 5 seconds
                       f"Max response time {max_time:.2f}s exceeds 5s")
        self.assertLess(total_time, 10.0,  # Total time < 10 seconds
                       f"Total execution time {total_time:.2f}s exceeds 10s")
    
    def test_concurrent_article_detail_requests(self):
        """
        Test article detail page performance with 100 concurrent requests.
        Target: All requests complete in < 3 seconds.
        """
        num_requests = 100
        article = self.articles[0]
        url = reverse('news_events:article-detail', kwargs={'slug': article.slug})
        results = []
        
        def make_request(request_id):
            """Make a single request and return timing."""
            start_time = time.time()
            try:
                client = Client()
                response = client.get(url)
                end_time = time.time()
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'status': 0,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        max_time = max(r['time'] for r in successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_requests * 0.95,
                               f"Only {len(successful)}/{num_requests} requests succeeded")
        self.assertLess(avg_time, 3.0,
                       f"Average response time {avg_time:.2f}s exceeds 3s")
        self.assertLess(max_time, 6.0,
                       f"Max response time {max_time:.2f}s exceeds 6s")
    
    def test_concurrent_api_requests(self):
        """
        Test API endpoint performance with 200 concurrent requests.
        Target: All requests complete in < 2 seconds.
        """
        from rest_framework.test import APIClient
        
        num_requests = 200
        url = reverse('news_events_api:article-list')
        results = []
        
        def make_request(request_id):
            """Make a single API request and return timing."""
            start_time = time.time()
            try:
                client = APIClient()
                response = client.get(url)
                end_time = time.time()
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'status': 0,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_requests * 0.95,
                               f"Only {len(successful)}/{num_requests} requests succeeded")
        self.assertLess(avg_time, 2.0,
                       f"Average API response time {avg_time:.2f}s exceeds 2s")
        self.assertLess(total_time, 15.0,
                       f"Total execution time {total_time:.2f}s exceeds 15s")


class CachePerformanceLoadTest(LoadTestBase):
    """
    Test cache performance under load.
    """
    
    def test_cache_hit_performance(self):
        """
        Test that cached responses are significantly faster than uncached.
        """
        url = reverse('news_events:home')
        
        # Clear cache and make first request (cache miss)
        cache.clear()
        start_time = time.time()
        response1 = self.client.get(url)
        uncached_time = time.time() - start_time
        self.assertEqual(response1.status_code, 200)
        
        # Make second request (cache hit)
        start_time = time.time()
        response2 = self.client.get(url)
        cached_time = time.time() - start_time
        self.assertEqual(response2.status_code, 200)
        
        # Cached request should be at least 50% faster
        self.assertLess(cached_time, uncached_time * 0.5,
                       f"Cached time {cached_time:.3f}s not significantly faster than uncached {uncached_time:.3f}s")
    
    def test_concurrent_cache_access(self):
        """
        Test cache performance with concurrent access.
        """
        url = reverse('news_events:home')
        num_requests = 50
        results = []
        
        # Populate cache first
        self.client.get(url)
        
        def make_request(request_id):
            """Make a cached request."""
            start_time = time.time()
            try:
                client = Client()
                response = client.get(url)
                end_time = time.time()
                return {
                    'id': request_id,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent cached requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Cached requests should be very fast
        self.assertGreaterEqual(len(successful), num_requests * 0.95)
        self.assertLess(avg_time, 0.5,  # Cached requests < 0.5 seconds
                       f"Average cached response time {avg_time:.3f}s exceeds 0.5s")


class DatabaseQueryLoadTest(LoadTestBase):
    """
    Test database query performance under load.
    """
    
    @override_settings(DEBUG=True)
    def test_query_count_under_load(self):
        """
        Test that query count remains reasonable under load.
        """
        from django.db import connection
        from django.test.utils import override_settings
        
        url = reverse('news_events:home')
        
        # Reset query count
        connection.queries_log.clear()
        
        # Make request and count queries
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        query_count = len(connection.queries)
        
        # Home page should use < 20 queries (with optimizations)
        self.assertLess(query_count, 20,
                       f"Query count {query_count} exceeds 20. Consider query optimization.")
    
    def test_concurrent_database_writes(self):
        """
        Test database write performance under concurrent load.
        """
        num_writes = 30
        results = []
        
        def create_comment(comment_id):
            """Create a comment concurrently."""
            start_time = time.time()
            try:
                article = self.articles[comment_id % len(self.articles)]
                comment = Comment.objects.create(
                    article=article,
                    author_name=f'Load Tester {comment_id}',
                    author_email=f'loadtest{comment_id}@example.com',
                    content=f'Load test comment {comment_id}',
                    status=Comment.Status.PENDING
                )
                end_time = time.time()
                return {
                    'id': comment_id,
                    'time': end_time - start_time,
                    'success': True,
                    'comment_id': comment.id
                }
            except Exception as e:
                return {
                    'id': comment_id,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent writes
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_comment, i) for i in range(num_writes)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_writes * 0.95)
        self.assertLess(avg_time, 1.0,  # Average write < 1 second
                       f"Average write time {avg_time:.3f}s exceeds 1s")
        self.assertLess(total_time, 10.0,  # Total time < 10 seconds
                       f"Total write time {total_time:.2f}s exceeds 10s")
        
        # Verify comments were created
        self.assertEqual(Comment.objects.count(), len(successful))


class ServiceLayerLoadTest(LoadTestBase):
    """
    Test service layer performance under load.
    """
    
    def test_concurrent_service_calls(self):
        """
        Test service layer performance with concurrent calls.
        """
        num_calls = 50
        results = []
        
        def call_service(call_id):
            """Call service method concurrently."""
            start_time = time.time()
            try:
                data = NewsService.get_home_page_data()
                end_time = time.time()
                return {
                    'id': call_id,
                    'time': end_time - start_time,
                    'success': 'recent_articles' in data
                }
            except Exception as e:
                return {
                    'id': call_id,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent service calls
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(call_service, i) for i in range(num_calls)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_calls * 0.95)
        self.assertLess(avg_time, 1.0,  # Average service call < 1 second
                       f"Average service call time {avg_time:.3f}s exceeds 1s")
        self.assertLess(total_time, 8.0,  # Total time < 8 seconds
                       f"Total service call time {total_time:.2f}s exceeds 8s")
    
    def test_concurrent_article_detail_service_calls(self):
        """
        Test article detail service performance with concurrent calls.
        """
        num_calls = 30
        article = self.articles[0]
        results = []
        
        def call_service(call_id):
            """Call article detail service concurrently."""
            start_time = time.time()
            try:
                data = NewsService.get_article_detail(article.slug)
                end_time = time.time()
                return {
                    'id': call_id,
                    'time': end_time - start_time,
                    'success': 'article' in data
                }
            except Exception as e:
                return {
                    'id': call_id,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent service calls
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(call_service, i) for i in range(num_calls)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_calls * 0.95)
        self.assertLess(avg_time, 1.5,  # Average service call < 1.5 seconds
                       f"Average article detail service time {avg_time:.3f}s exceeds 1.5s")


class SearchLoadTest(LoadTestBase):
    """
    Test search functionality performance under load.
    """
    
    def test_concurrent_search_requests(self):
        """
        Test search performance with concurrent requests.
        """
        num_requests = 40
        results = []
        
        def perform_search(request_id):
            """Perform search concurrently."""
            start_time = time.time()
            try:
                client = Client()
                response = client.get(
                    reverse('news_events:search'),
                    {'q': f'test {request_id % 10}'}  # Vary search terms
                )
                end_time = time.time()
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'status': 0,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent searches
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(perform_search, i) for i in range(num_requests)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_requests * 0.95)
        self.assertLess(avg_time, 2.0,  # Average search < 2 seconds
                       f"Average search time {avg_time:.3f}s exceeds 2s")
        self.assertLess(total_time, 12.0,  # Total time < 12 seconds
                       f"Total search time {total_time:.2f}s exceeds 12s")


class SubscriptionLoadTest(LoadTestBase):
    """
    Test subscription functionality performance under load.
    """
    
    def test_concurrent_subscriptions(self):
        """
        Test subscription creation performance with concurrent requests.
        """
        num_subscriptions = 25
        results = []
        
        def create_subscription(sub_id):
            """Create subscription concurrently."""
            start_time = time.time()
            try:
                client = Client()
                response = client.post(
                    reverse('news_events:subscribe'),
                    {
                        'email': f'loadtest{sub_id}@example.com',
                        'name': f'Load Tester {sub_id}'
                    }
                )
                end_time = time.time()
                return {
                    'id': sub_id,
                    'status': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code in [200, 201, 302]
                }
            except Exception as e:
                return {
                    'id': sub_id,
                    'status': 0,
                    'time': time.time() - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # Execute concurrent subscriptions
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_subscription, i) for i in range(num_subscriptions)]
            for future in as_completed(futures):
                results.append(future.result())
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        
        # Assertions
        self.assertGreaterEqual(len(successful), num_subscriptions * 0.90)  # 90% success (some may be duplicates)
        self.assertLess(avg_time, 1.5,  # Average subscription < 1.5 seconds
                       f"Average subscription time {avg_time:.3f}s exceeds 1.5s")
        self.assertLess(total_time, 8.0,  # Total time < 8 seconds
                       f"Total subscription time {total_time:.2f}s exceeds 8s")


class MemoryLeakLoadTest(LoadTestBase):
    """
    Test for memory leaks under sustained load.
    """
    
    def test_sustained_request_load(self):
        """
        Test that system doesn't leak memory under sustained load.
        """
        url = reverse('news_events:home')
        num_iterations = 100
        
        # Make many requests in sequence
        times = []
        for i in range(num_iterations):
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            times.append(end_time - start_time)
            self.assertEqual(response.status_code, 200)
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        first_half_avg = sum(times[:len(times)//2]) / (len(times)//2)
        second_half_avg = sum(times[len(times)//2:]) / (len(times) - len(times)//2)
        
        # Performance shouldn't degrade significantly (no more than 50% slower)
        performance_degradation = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0
        self.assertLess(performance_degradation, 0.5,
                       f"Performance degraded by {performance_degradation*100:.1f}%. Possible memory leak.")


class ResponseTimeBenchmarkTest(LoadTestBase):
    """
    Benchmark response times for different endpoints.
    """
    
    def test_response_time_benchmarks(self):
        """
        Test that all endpoints meet performance benchmarks.
        """
        benchmarks = {
            'home': {
                'url': reverse('news_events:home'),
                'max_time': 2.0,
                'iterations': 10
            },
            'article_list': {
                'url': reverse('news_events:article-list'),
                'max_time': 1.5,
                'iterations': 10
            },
            'event_list': {
                'url': reverse('news_events:event-list'),
                'max_time': 1.5,
                'iterations': 10
            },
            'search': {
                'url': reverse('news_events:search'),
                'max_time': 2.0,
                'iterations': 10
            },
        }
        
        results = {}
        
        for endpoint_name, config in benchmarks.items():
            times = []
            for _ in range(config['iterations']):
                start_time = time.time()
                response = self.client.get(config['url'])
                end_time = time.time()
                self.assertEqual(response.status_code, 200)
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            results[endpoint_name] = {
                'avg': avg_time,
                'max': max_time
            }
            
            # Assert benchmark
            self.assertLess(avg_time, config['max_time'],
                           f"{endpoint_name} average time {avg_time:.3f}s exceeds benchmark {config['max_time']}s")
        
        # Print results for debugging
        print("\nPerformance Benchmarks:")
        for endpoint, metrics in results.items():
            print(f"  {endpoint}: avg={metrics['avg']:.3f}s, max={metrics['max']:.3f}s")

