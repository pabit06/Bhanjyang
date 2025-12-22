"""
Tests for services app calculator_views module
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.forms import Form
from unittest.mock import patch, MagicMock

from apps.services.calculator_views import BaseCalculatorView
from apps.services.utils import FinancialCalculator


class TestCalculatorForm(Form):
    """Test form for calculator"""
    principal = None
    rate = None
    tenure = None


class TestCalculatorView(BaseCalculatorView):
    """Test calculator view implementation"""
    form_class = TestCalculatorForm
    template_name = 'services/test_calculator.html'
    page_title = 'Test Calculator'
    page_description = 'Test calculator description'
    calculator_type = 'test'
    service_type = 'test'
    
    def perform_calculation(self, form):
        """Test calculation implementation"""
        return {'result': 'test'}, None


class BaseCalculatorViewTest(TestCase):
    """Test BaseCalculatorView"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.view = TestCalculatorView()
    
    def test_get_form(self):
        """Test getting form for GET request"""
        request = self.factory.get('/calculator/')
        form = self.view.get_form(request)
        self.assertIsInstance(form, TestCalculatorForm)
    
    def test_get_form_with_data(self):
        """Test getting form with POST data"""
        request = self.factory.post('/calculator/', {'principal': '100000'})
        form = self.view.get_form_with_data(request)
        self.assertIsInstance(form, TestCalculatorForm)
    
    def test_perform_calculation_not_implemented(self):
        """Test that perform_calculation raises NotImplementedError in base class"""
        base_view = BaseCalculatorView()
        form = TestCalculatorForm()
        with self.assertRaises(NotImplementedError):
            base_view.perform_calculation(form)
    
    def test_track_usage(self):
        """Test tracking usage"""
        with patch('apps.services.calculator_views.ServiceAnalyticsService.track_usage') as mock_track:
            self.view.track_usage(service_id=1)
            mock_track.assert_called_once_with('test', 1, 'calculator_usage')
    
    def test_get_context_data(self):
        """Test getting context data"""
        form = TestCalculatorForm()
        context = self.view.get_context_data(form)
        self.assertIn('form', context)
        self.assertIn('page_title', context)
        self.assertIn('page_description', context)
        self.assertIn('breadcrumbs', context)
        self.assertEqual(context['page_title'], 'Test Calculator')
    
    def test_get_context_data_with_calculation(self):
        """Test getting context data with calculation"""
        form = TestCalculatorForm()
        calculation = {'result': 'test'}
        context = self.view.get_context_data(form, calculation=calculation)
        self.assertIn('calculation', context)
        self.assertEqual(context['calculation'], calculation)
    
    def test_get_context_data_with_service_obj(self):
        """Test getting context data with service object"""
        form = TestCalculatorForm()
        service_obj = MagicMock()
        service_obj.id = 1
        context = self.view.get_context_data(form, service_obj=service_obj)
        self.assertIn('test_type', context)
        self.assertEqual(context['test_type'], service_obj)
    
    def test_get_method(self):
        """Test GET request handling"""
        request = self.factory.get('/calculator/')
        request.user = self.user
        with patch('apps.services.calculator_views.render') as mock_render:
            mock_render.return_value = MagicMock()
            response = self.view.get(request)
            mock_render.assert_called_once()
            args, kwargs = mock_render.call_args
            self.assertEqual(kwargs['template_name'], 'services/test_calculator.html')
            self.assertIn('form', kwargs['context'])
    
    def test_post_method_valid_form(self):
        """Test POST request with valid form"""
        request = self.factory.post('/calculator/', {})
        request.user = self.user
        with patch('apps.services.calculator_views.render') as mock_render, \
             patch.object(self.view, 'perform_calculation') as mock_calc:
            mock_calc.return_value = ({'result': 'test'}, None)
            mock_render.return_value = MagicMock()
            # Mock form validation
            with patch.object(TestCalculatorForm, 'is_valid', return_value=True):
                form = TestCalculatorForm()
                form.is_valid = lambda: True
                with patch.object(self.view, 'get_form_with_data', return_value=form):
                    response = self.view.post(request)
                    mock_render.assert_called_once()
    
    def test_post_method_invalid_form(self):
        """Test POST request with invalid form"""
        request = self.factory.post('/calculator/', {})
        request.user = self.user
        with patch('apps.services.calculator_views.render') as mock_render:
            mock_render.return_value = MagicMock()
            # Mock form validation
            with patch.object(TestCalculatorForm, 'is_valid', return_value=False):
                form = TestCalculatorForm()
                form.is_valid = lambda: False
                with patch.object(self.view, 'get_form_with_data', return_value=form):
                    response = self.view.post(request)
                    mock_render.assert_called_once()
                    # Should not call perform_calculation
                    args, kwargs = mock_render.call_args
                    self.assertIn('form', kwargs['context'])
                    self.assertNotIn('calculation', kwargs['context'])
    
    def test_track_usage_with_service_id(self):
        """Test tracking usage when service object has ID"""
        request = self.factory.post('/calculator/', {})
        request.user = self.user
        service_obj = MagicMock()
        service_obj.id = 1
        
        with patch('apps.services.calculator_views.ServiceAnalyticsService.track_usage') as mock_track, \
             patch('apps.services.calculator_views.render') as mock_render, \
             patch.object(self.view, 'perform_calculation') as mock_calc:
            mock_calc.return_value = ({'result': 'test'}, service_obj)
            mock_render.return_value = MagicMock()
            form = TestCalculatorForm()
            form.is_valid = lambda: True
            with patch.object(self.view, 'get_form_with_data', return_value=form):
                self.view.post(request)
                mock_track.assert_called_once_with('test', 1, 'calculator_usage')
    
    def test_track_usage_without_service_id(self):
        """Test tracking usage when service object has no ID"""
        request = self.factory.post('/calculator/', {})
        request.user = self.user
        service_obj = MagicMock()
        del service_obj.id  # Remove id attribute
        
        with patch('apps.services.calculator_views.ServiceAnalyticsService.track_usage') as mock_track, \
             patch('apps.services.calculator_views.render') as mock_render, \
             patch.object(self.view, 'perform_calculation') as mock_calc:
            mock_calc.return_value = ({'result': 'test'}, service_obj)
            mock_render.return_value = MagicMock()
            form = TestCalculatorForm()
            form.is_valid = lambda: True
            with patch.object(self.view, 'get_form_with_data', return_value=form):
                self.view.post(request)
                # Should not track usage if no ID
                mock_track.assert_not_called()

