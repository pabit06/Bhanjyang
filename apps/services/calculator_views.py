"""
Base calculator view class to reduce code duplication.
"""
from typing import Dict, Any, Optional, Type, Tuple
from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.forms import Form
from .utils import FinancialCalculator
from .services import ServiceAnalyticsService
from apps.core.view_mixins import NepaliLanguageMixin, create_breadcrumbs


class BaseCalculatorView(NepaliLanguageMixin, View):
    """Base class for calculator views to reduce duplication."""
    
    form_class: Type[Form]
    template_name: str
    page_title: str
    page_description: str
    calculator_type: str  # 'loan', 'savings', 'fixed_deposit'
    service_type: str  # 'loan', 'savings', 'fixed_deposit'
    
    def get_form(self, request: HttpRequest) -> Form:
        """Get form instance for GET requests."""
        return self.form_class()
    
    def get_form_with_data(self, request: HttpRequest) -> Form:
        """Get form instance with POST data."""
        return self.form_class(request.POST)
    
    def perform_calculation(self, form: Form) -> Tuple[Dict[str, Any], Any]:
        """
        Perform the calculation based on form data.
        Must be implemented by subclasses.
        
        Returns:
            Tuple of (calculation_dict, service_object)
        """
        raise NotImplementedError("Subclasses must implement perform_calculation")
    
    def track_usage(self, service_id: int) -> None:
        """Track calculator usage."""
        ServiceAnalyticsService.track_usage(
            self.service_type, 
            service_id, 
            'calculator_usage'
        )
    
    def get_context_data(
        self, 
        form: Form, 
        calculation: Optional[Dict[str, Any]] = None,
        service_obj: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Build context dictionary for template."""
        context = {
            'form': form,
            'page_title': self.page_title,
            'page_description': self.page_description,
            'breadcrumbs': create_breadcrumbs(
                ('Home', '/'),
                ('Services', '/services/'),
                (self.page_title, None)
            )
        }
        
        if calculation:
            context['calculation'] = calculation
        
        if service_obj:
            context[f'{self.service_type}_type'] = service_obj
        
        return context
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET requests."""
        form = self.get_form(request)
        context = self.get_context_data(form)
        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle POST requests."""
        form = self.get_form_with_data(request)
        
        if form.is_valid():
            calculation, service_obj = self.perform_calculation(form)
            
            # Track usage if service object has ID
            if service_obj and hasattr(service_obj, 'id'):
                self.track_usage(service_obj.id)
            
            context = self.get_context_data(form, calculation, service_obj)
            return render(request, self.template_name, context)
        else:
            context = self.get_context_data(form)
            return render(request, self.template_name, context)

