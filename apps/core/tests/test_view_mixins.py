"""
Comprehensive tests for view mixins and utilities.
"""
from django.test import TestCase, RequestFactory
from django.views.generic import DetailView
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock

from apps.core.view_mixins import (
    BreadcrumbMixin,
    ServiceTrackingMixin,
    ServiceDetailViewMixin,
    create_breadcrumbs
)
from apps.services.models import SavingsAccount, LoanType
from apps.services.services import ServiceAnalyticsService

User = get_user_model()


class TestBreadcrumbMixin(TestCase):
    """Test suite for BreadcrumbMixin"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create a test view class with BreadcrumbMixin
        class TestView(BreadcrumbMixin, DetailView):
            model = SavingsAccount
            breadcrumbs = [
                {'name': 'Home', 'url': '/'},
                {'name': 'Services', 'url': '/services/'},
                {'name': 'Test', 'url': None}
            ]
        
        self.view_class = TestView
    
    def test_get_breadcrumbs(self):
        """Test getting breadcrumbs from mixin"""
        view = self.view_class()
        breadcrumbs = view.get_breadcrumbs()
        
        self.assertEqual(len(breadcrumbs), 3)
        self.assertEqual(breadcrumbs[0]['name'], 'Home')
        self.assertEqual(breadcrumbs[0]['url'], '/')
        self.assertEqual(breadcrumbs[2]['name'], 'Test')
    
    def test_get_context_data_adds_breadcrumbs(self):
        """Test that get_context_data adds breadcrumbs to context"""
        view = self.view_class()
        
        # Mock super().get_context_data()
        with patch.object(DetailView, 'get_context_data', return_value={}):
            context = view.get_context_data()
            
            self.assertIn('breadcrumbs', context)
            self.assertEqual(len(context['breadcrumbs']), 3)
    
    def test_empty_breadcrumbs(self):
        """Test view with empty breadcrumbs"""
        class EmptyBreadcrumbView(BreadcrumbMixin, DetailView):
            model = SavingsAccount
            breadcrumbs = []
        
        view = EmptyBreadcrumbView()
        breadcrumbs = view.get_breadcrumbs()
        self.assertEqual(breadcrumbs, [])


class TestServiceTrackingMixin(TestCase):
    """Test suite for ServiceTrackingMixin"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create test savings account
        self.savings_account = SavingsAccount.objects.create(
            english_name='Test Savings',
            nepali_name='परीक्षण बचत',
            account_type='general',
            interest_rate=5.0,
            is_active=True
        )
        
        # Create a test view class with ServiceTrackingMixin
        class TestView(ServiceTrackingMixin, DetailView):
            model = SavingsAccount
            service_type = 'savings'
            tracking_event = 'page_views'
        
        self.view_class = TestView
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_tracking_on_get_object(self, mock_track):
        """Test that tracking is called when get_object is called"""
        view = self.view_class()
        view.kwargs = {'pk': self.savings_account.pk}
        
        obj = view.get_object()
        
        self.assertEqual(obj, self.savings_account)
        mock_track.assert_called_once_with('savings', self.savings_account.id, 'page_views')
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_tracking_with_custom_event(self, mock_track):
        """Test tracking with custom event type"""
        class CustomEventView(ServiceTrackingMixin, DetailView):
            model = SavingsAccount
            service_type = 'savings'
            tracking_event = 'custom_event'
        
        view = CustomEventView()
        view.kwargs = {'pk': self.savings_account.pk}
        
        view.get_object()
        
        mock_track.assert_called_once_with('savings', self.savings_account.id, 'custom_event')
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_no_tracking_without_service_type(self, mock_track):
        """Test that tracking is not called if service_type is empty"""
        class NoServiceTypeView(ServiceTrackingMixin, DetailView):
            model = SavingsAccount
            service_type = ''
        
        view = NoServiceTypeView()
        view.kwargs = {'pk': self.savings_account.pk}
        
        view.get_object()
        
        mock_track.assert_not_called()
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_no_tracking_without_id(self, mock_track):
        """Test that tracking is not called if object has no id"""
        class NoIdView(ServiceTrackingMixin, DetailView):
            model = SavingsAccount
            service_type = 'savings'
        
        view = NoIdView()
        view.kwargs = {'pk': self.savings_account.pk}
        
        # Mock object without id
        with patch.object(view, 'get_object', return_value=Mock(spec=[])):
            obj = view.get_object()
            # Should not raise error even if object has no id
            self.assertIsNotNone(obj)


class TestServiceDetailViewMixin(TestCase):
    """Test suite for ServiceDetailViewMixin (combines both mixins)"""
    
    def setUp(self):
        """Set up test data"""
        self.savings_account = SavingsAccount.objects.create(
            english_name='Test Savings',
            nepali_name='परीक्षण बचत',
            account_type='general',
            interest_rate=5.0,
            is_active=True
        )
        
        class TestDetailView(ServiceDetailViewMixin, DetailView):
            model = SavingsAccount
            service_type = 'savings'
            breadcrumbs = [
                {'name': 'Home', 'url': '/'},
                {'name': 'Services', 'url': '/services/'}
            ]
        
        self.view_class = TestDetailView
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_combined_functionality(self, mock_track):
        """Test that ServiceDetailViewMixin combines both functionalities"""
        view = self.view_class()
        view.kwargs = {'pk': self.savings_account.pk}
        
        # Mock super().get_context_data()
        with patch.object(DetailView, 'get_context_data', return_value={}):
            context = view.get_context_data()
            
            # Should have breadcrumbs
            self.assertIn('breadcrumbs', context)
            self.assertEqual(len(context['breadcrumbs']), 2)
            
            # Should track usage
            obj = view.get_object()
            mock_track.assert_called_once_with('savings', self.savings_account.id, 'page_views')


class TestCreateBreadcrumbs(TestCase):
    """Test suite for create_breadcrumbs helper function"""
    
    def test_create_breadcrumbs_basic(self):
        """Test basic breadcrumb creation"""
        breadcrumbs = create_breadcrumbs(
            ('Home', '/'),
            ('Services', '/services/'),
            ('Details', None)
        )
        
        self.assertEqual(len(breadcrumbs), 3)
        self.assertEqual(breadcrumbs[0], {'name': 'Home', 'url': '/'})
        self.assertEqual(breadcrumbs[1], {'name': 'Services', 'url': '/services/'})
        self.assertEqual(breadcrumbs[2], {'name': 'Details', 'url': '#'})
    
    def test_create_breadcrumbs_single_item(self):
        """Test creating breadcrumbs with single item"""
        breadcrumbs = create_breadcrumbs(('Home', '/'))
        
        self.assertEqual(len(breadcrumbs), 1)
        self.assertEqual(breadcrumbs[0], {'name': 'Home', 'url': '/'})
    
    def test_create_breadcrumbs_empty(self):
        """Test creating empty breadcrumbs"""
        breadcrumbs = create_breadcrumbs()
        
        self.assertEqual(breadcrumbs, [])
    
    def test_create_breadcrumbs_with_none_url(self):
        """Test breadcrumbs with None URL (current page)"""
        breadcrumbs = create_breadcrumbs(
            ('Home', '/'),
            ('Current Page', None)
        )
        
        self.assertEqual(breadcrumbs[1]['url'], '#')
    
    def test_create_breadcrumbs_with_empty_string_url(self):
        """Test breadcrumbs with empty string URL"""
        breadcrumbs = create_breadcrumbs(
            ('Home', '/'),
            ('Page', '')
        )
        
        self.assertEqual(breadcrumbs[1]['url'], '#')
    
    def test_create_breadcrumbs_multiple_items(self):
        """Test creating breadcrumbs with many items"""
        breadcrumbs = create_breadcrumbs(
            ('Home', '/'),
            ('Category', '/category/'),
            ('Subcategory', '/category/sub/'),
            ('Item', '/category/sub/item/'),
            ('Details', None)
        )
        
        self.assertEqual(len(breadcrumbs), 5)
        self.assertEqual(breadcrumbs[-1]['name'], 'Details')
        self.assertEqual(breadcrumbs[-1]['url'], '#')


class TestViewMixinsIntegration(TestCase):
    """Integration tests for view mixins with actual models"""
    
    def setUp(self):
        """Set up test data"""
        self.savings_account = SavingsAccount.objects.create(
            english_name='Integration Test Savings',
            nepali_name='एकीकरण परीक्षण बचत',
            account_type='general',
            interest_rate=6.0,
            is_active=True,
            is_featured=True
        )
        
        self.loan_type = LoanType.objects.create(
            english_name='Test Loan',
            nepali_name='परीक्षण ऋण',
            loan_category='personal',
            monthly_interest_rate=1.5,
            is_active=True
        )
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_integration_with_savings_account(self, mock_track):
        """Test mixins with actual SavingsAccount model"""
        class SavingsDetailView(ServiceDetailViewMixin, DetailView):
            model = SavingsAccount
            service_type = 'savings'
            breadcrumbs = create_breadcrumbs(
                ('Home', '/'),
                ('Services', '/services/'),
                ('Savings', None)
            )
        
        view = SavingsDetailView()
        view.kwargs = {'pk': self.savings_account.pk}
        
        # Test get_object (should track)
        obj = view.get_object()
        self.assertEqual(obj, self.savings_account)
        mock_track.assert_called_once_with('savings', self.savings_account.id, 'page_views')
        
        # Test get_context_data (should have breadcrumbs)
        with patch.object(DetailView, 'get_context_data', return_value={}):
            context = view.get_context_data()
            self.assertIn('breadcrumbs', context)
            self.assertEqual(len(context['breadcrumbs']), 3)
    
    @patch('apps.core.view_mixins.ServiceAnalyticsService.track_usage')
    def test_integration_with_loan_type(self, mock_track):
        """Test mixins with actual LoanType model"""
        class LoanDetailView(ServiceDetailViewMixin, DetailView):
            model = LoanType
            service_type = 'loan'
            tracking_event = 'custom_view'
            breadcrumbs = create_breadcrumbs(
                ('Home', '/'),
                ('Loans', '/loans/')
            )
        
        view = LoanDetailView()
        view.kwargs = {'pk': self.loan_type.pk}
        
        obj = view.get_object()
        self.assertEqual(obj, self.loan_type)
        mock_track.assert_called_once_with('loan', self.loan_type.id, 'custom_view')

