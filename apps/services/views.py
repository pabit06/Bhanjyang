from typing import Dict, Any, Optional, Type, Tuple
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, RedirectView
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import Form
import json
import random
from datetime import date
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, MemberRelief, DigitalService
)

# Service type to model mapping for service_application view
SERVICE_MODEL_MAPPING = {
    'savings': SavingsAccount,
    'loan': LoanType,
    'fixed_deposit': FixedDeposit,
    'remittance': RemittanceService,
    'relief': MemberRelief,
    'digital': DigitalService
}
from .forms import (
    LoanCalculatorForm, SavingsCalculatorForm, FixedDepositCalculatorForm,
    ServiceApplicationForm, ServiceComparisonForm, ServiceSearchForm, ServiceRecommendationForm
)
from .utils import FinancialCalculator
from .services import (
    ServiceAnalyticsService, ServiceRecommendationService,
    ServiceComparisonService, ServiceSearchService, ServiceApplicationService
)
from apps.core.error_handling import (
    ErrorResponse, ErrorLogger, handle_api_errors, safe_json_parse,
    safe_float_conversion, safe_int_conversion
)
from apps.core.view_mixins import ServiceDetailViewMixin, NepaliLanguageMixin, create_breadcrumbs
from apps.core.query_utils import get_active_queryset, get_featured_queryset
from django.utils.translation import activate, gettext as _


class ServicesOverviewView(RedirectView):
    """Redirect services overview to savings list page"""
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        from django.urls import reverse
        return reverse('services:savings_list')


class SavingsAccountsView(NepaliLanguageMixin, ListView):
    """Display all savings account types"""
    model = SavingsAccount
    template_name = 'services/savings/savings_list.html'
    context_object_name = 'savings_accounts'
    
    def get_queryset(self):
        return SavingsAccount.objects.filter(is_active=True).order_by('-is_featured', 'interest_rate', 'account_type').only(
            'id', 'english_name', 'nepali_name', 'slug', 'account_type', 
            'interest_rate', 'minimum_balance', 'is_featured', 'icon', 'color', 'description'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Savings Accounts'
        context['page_description'] = 'Choose from our range of savings accounts with competitive interest rates'
        
        # Add breadcrumbs
        from apps.core.view_mixins import create_breadcrumbs
        from django.utils.translation import gettext_lazy as _
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('Services'), 'services:overview'),
            (_('Savings Accounts'), 'services:savings_list')
        )
        
        # Get all active savings accounts with optimized field selection
        all_savings = SavingsAccount.objects.filter(is_active=True).order_by('category', '-interest_rate').only(
            'id', 'english_name', 'nepali_name', 'slug', 'account_type', 'category',
            'interest_rate', 'minimum_balance', 'is_featured', 'icon', 'color', 'description'
        )
        
        # Group by category
        context['regular_savings'] = all_savings.filter(category='regular')
        context['optional_savings'] = all_savings.filter(category='optional')
        context['recurring_savings'] = all_savings.filter(category='recurring')
        
        # Periodic Savings (Fixed Deposits) with optimized fields
        context['periodic_savings'] = FixedDeposit.objects.filter(is_active=True).order_by('duration_months').only(
            'id', 'english_name', 'nepali_name', 'slug', 'duration_months',
            'interest_rate', 'payment_frequency', 'is_featured', 'icon', 'color', 'description'
        )
        
        context['featured_accounts'] = all_savings.filter(is_featured=True)
        return context


class FixedDepositsView(RedirectView):
    """Redirect fixed deposits page to savings page (आवधिक बचत section)"""
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        from django.urls import reverse
        # Redirect to savings page with anchor to periodic savings section
        return reverse('services:savings_list') + '#periodic-savings'


class LoanServicesView(NepaliLanguageMixin, ListView):
    """Display all loan services"""
    model = LoanType
    template_name = 'services/loan/loan_list.html'
    context_object_name = 'loan_types'
    
    def get_queryset(self):
        return LoanType.objects.filter(is_active=True).order_by('-is_featured', 'loan_category').only(
            'id', 'english_name', 'nepali_name', 'slug', 'loan_category',
            'monthly_interest_rate', 'is_featured', 'icon', 'color', 'description',
            'minimum_amount', 'maximum_amount', 'max_tenure_years'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Loan Services'
        context['page_description'] = 'Flexible loan options for all your financial needs'
        
        # Add breadcrumbs
        from django.utils.translation import gettext_lazy as _
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('Services'), 'services:overview'),
            (_('Loan Services'), 'services:loan_list')
        )
        
        context['featured_loans'] = LoanType.objects.filter(is_active=True, is_featured=True).only(
            'id', 'english_name', 'nepali_name', 'slug', 'loan_category',
            'monthly_interest_rate', 'is_featured', 'icon', 'color', 'description', 'benefits'
        )
        return context


class RemittanceServicesView(NepaliLanguageMixin, ListView):
    """Display remittance services"""
    model = RemittanceService
    template_name = 'services/remittance/remittance_list.html'
    context_object_name = 'remittance_services'
    
    def get_queryset(self):
        # Exclude mobile_banking as it belongs to digital services
        return RemittanceService.objects.filter(
            is_active=True
        ).exclude(
            service_type='mobile_banking'
        ).order_by('service_type', 'english_name').only(
            'id', 'english_name', 'nepali_name', 'slug', 'service_type',
            'is_featured', 'icon', 'color', 'description', 'processing_time', 'fees'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remittance Services'
        context['page_description'] = 'Available remittance services for receiving money from abroad'
        
        # Add breadcrumbs
        from django.utils.translation import gettext_lazy as _
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('Services'), 'services:overview'),
            (_('Remittance Services'), 'services:remittance_list')
        )
        
        # Get featured remittances (excluding mobile_banking)
        context['featured_remittances'] = RemittanceService.objects.filter(
            is_active=True, 
            is_featured=True
        ).exclude(
            service_type='mobile_banking'
        ).only(
            'id', 'english_name', 'nepali_name', 'slug', 'service_type',
            'is_featured', 'icon', 'color', 'description', 'processing_time', 'fees'
        )
        
        # Group remittances by service type (already optimized in get_queryset)
        queryset = self.get_queryset()
        context['international_remittances'] = queryset.filter(service_type='international')
        context['domestic_remittances'] = queryset.filter(service_type='domestic')
        
        return context


class MemberReliefView(NepaliLanguageMixin, ListView):
    """Display member relief programs"""
    model = MemberRelief
    template_name = 'services/member_relief/member_relief_list.html'
    context_object_name = 'member_reliefs'
    
    def get_queryset(self):
        return MemberRelief.objects.filter(is_active=True).order_by('relief_type', 'english_name').only(
            'id', 'english_name', 'nepali_name', 'slug', 'relief_type',
            'is_featured', 'icon', 'color', 'description', 'eligibility', 'benefits'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Member Relief Programs'
        context['page_description'] = 'Support and assistance programs for our valued members'
        
        # Add breadcrumbs
        from django.utils.translation import gettext_lazy as _
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('Services'), 'services:overview'),
            (_('Member Relief'), 'services:member_relief_list')
        )
        
        # Group by relief type
        reliefs_by_type = {}
        for relief in context['member_reliefs']:
            relief_type = relief.get_relief_type_display()
            if relief_type not in reliefs_by_type:
                reliefs_by_type[relief_type] = []
            reliefs_by_type[relief_type].append(relief)
        
        context['reliefs_by_type'] = reliefs_by_type
        return context


# --- Detail Views (Refactored with Mixins) ---

class SavingsDetailView(NepaliLanguageMixin, ServiceDetailViewMixin, DetailView):
    """Display details for a specific savings account."""
    model = SavingsAccount
    template_name = 'services/savings/savings_detail.html'
    context_object_name = 'service'
    service_type = 'savings'
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('Services', '/services/'),
        ('Savings Account', None)
    )
    
    def get_context_data(self, **kwargs):
        """Add related savings accounts to context."""
        context = super().get_context_data(**kwargs)
        # Get 3 random active savings accounts excluding the current one
        # Performance optimization: Get IDs first, then randomly select in Python
        active_ids = list(
            SavingsAccount.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .values_list('id', flat=True)
        )
        
        if active_ids:
            # Randomly select up to 3 IDs in Python (much faster than DB random sort)
            random_ids = random.sample(active_ids, min(len(active_ids), 3))
            # Fetch only the selected accounts with optimized field selection
            context['related_savings'] = SavingsAccount.objects.filter(
                id__in=random_ids
            ).only(
                'id', 'english_name', 'nepali_name', 'slug', 'account_type',
                'interest_rate', 'is_featured', 'icon', 'color', 'description',
                'minimum_balance'
            )
        else:
            context['related_savings'] = SavingsAccount.objects.none()
        
        return context


class LoanDetailView(NepaliLanguageMixin, ServiceDetailViewMixin, DetailView):
    """Display details for a specific loan type."""
    model = LoanType
    template_name = 'services/loan/loan_detail.html'
    context_object_name = 'service'
    service_type = 'loan'
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('Services', '/services/'),
        ('Loan Details', None)
    )
    
    def get_queryset(self):
        """Prefetch carousel images for better performance."""
        return LoanType.objects.prefetch_related('carousel_images').filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        """Add related loans to context."""
        context = super().get_context_data(**kwargs)
        # Get 3 random active loans excluding the current one
        # Performance optimization: Get IDs first, then randomly select in Python
        # This avoids expensive database random sorting (order_by('?'))
        active_ids = list(
            LoanType.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .values_list('id', flat=True)
        )
        
        if active_ids:
            # Randomly select up to 3 IDs in Python (much faster than DB random sort)
            random_ids = random.sample(active_ids, min(len(active_ids), 3))
            # Fetch only the selected loans with optimized field selection
            context['related_loans'] = LoanType.objects.filter(
                id__in=random_ids
            ).only(
                'id', 'english_name', 'nepali_name', 'slug', 'loan_category',
                'monthly_interest_rate', 'is_featured', 'icon', 'color', 'description',
                'minimum_amount', 'maximum_amount', 'max_tenure_years'
            )
        else:
            context['related_loans'] = LoanType.objects.none()
        
        return context


class FixedDepositDetailView(NepaliLanguageMixin, ServiceDetailViewMixin, DetailView):
    """Display details for a specific fixed deposit scheme."""
    model = FixedDeposit
    template_name = 'services/savings/fixed_deposit/detail.html'
    context_object_name = 'service'
    service_type = 'fixed_deposit'
    # Base mixin handles slug lookup automatically
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('Services', '/services/'),
        ('Fixed Deposit', None)
    )
    
    def get_context_data(self, **kwargs):
        """Add related fixed deposits to context."""
        context = super().get_context_data(**kwargs)
        # Get 3 random active fixed deposits excluding the current one
        active_ids = list(
            FixedDeposit.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .values_list('id', flat=True)
        )
        
        if active_ids:
            random_ids = random.sample(active_ids, min(len(active_ids), 3))
            context['related_deposits'] = FixedDeposit.objects.filter(
                id__in=random_ids
            ).only(
                'id', 'english_name', 'nepali_name', 'slug', 'duration_months',
                'interest_rate', 'payment_frequency', 'is_featured', 'icon', 'color', 'description'
            )
        else:
            context['related_deposits'] = FixedDeposit.objects.none()
        
        return context


class RemittanceDetailView(NepaliLanguageMixin, ServiceDetailViewMixin, DetailView):
    """Display details for a specific remittance service."""
    model = RemittanceService
    template_name = 'services/remittance/remittance_detail.html'
    context_object_name = 'service'
    service_type = 'remittance'
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('Services', '/services/'),
        ('Remittance Service', None)
    )
    
    def get_context_data(self, **kwargs):
        """Add related remittance services to context."""
        context = super().get_context_data(**kwargs)
        # Get 3 random active remittance services excluding the current one
        active_ids = list(
            RemittanceService.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .exclude(service_type='mobile_banking')
            .values_list('id', flat=True)
        )
        
        if active_ids:
            random_ids = random.sample(active_ids, min(len(active_ids), 3))
            context['related_remittances'] = RemittanceService.objects.filter(
                id__in=random_ids
            ).only(
                'id', 'english_name', 'nepali_name', 'slug', 'service_type',
                'is_featured', 'icon', 'color', 'description', 'processing_time', 'fees'
            )
        else:
            context['related_remittances'] = RemittanceService.objects.none()
        
        return context


class MemberReliefDetailView(NepaliLanguageMixin, ServiceDetailViewMixin, DetailView):
    """Display details for a specific member relief program."""
    model = MemberRelief
    template_name = 'services/member_relief/member_relief_detail.html'
    context_object_name = 'service'
    service_type = 'relief'
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('Services', '/services/'),
        ('Member Relief', None)
    )
    
    def get_context_data(self, **kwargs):
        """Add related relief programs to context."""
        context = super().get_context_data(**kwargs)
        # Get 3 random active relief programs excluding the current one
        active_ids = list(
            MemberRelief.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .values_list('id', flat=True)
        )
        
        if active_ids:
            random_ids = random.sample(active_ids, min(len(active_ids), 3))
            context['related_reliefs'] = MemberRelief.objects.filter(
                id__in=random_ids
            ).only(
                'id', 'english_name', 'nepali_name', 'slug', 'relief_type',
                'is_featured', 'icon', 'color', 'description', 'eligibility', 'benefits'
            )
        else:
            context['related_reliefs'] = MemberRelief.objects.none()
        
        return context


class DigitalServicesView(NepaliLanguageMixin, ListView):
    """Display digital services"""
    model = DigitalService
    template_name = 'services/digital/digital_list.html'
    context_object_name = 'digital_services'
    
    def get_queryset(self):
        return DigitalService.objects.filter(is_active=True).order_by('service_type', 'english_name').only(
            'id', 'english_name', 'nepali_name', 'slug', 'service_type',
            'is_featured', 'icon', 'color', 'description', 'features'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Digital Services'
        context['page_description'] = 'Modern digital banking solutions for your convenience'
        
        # Add breadcrumbs
        from django.utils.translation import gettext_lazy as _
        context['breadcrumbs'] = create_breadcrumbs(
            (_('Home'), 'home:index'),
            (_('Services'), 'services:overview'),
            (_('Digital Services'), 'services:digital_list')
        )
        
        # Group by service type
        services_by_type = {}
        for service in context['digital_services']:
            service_type = service.get_service_type_display()
            if service_type not in services_by_type:
                services_by_type[service_type] = []
            services_by_type[service_type].append(service)
        
        context['services_by_type'] = services_by_type
        
        context['featured_digital'] = DigitalService.objects.filter(is_active=True, is_featured=True).only(
            'id', 'english_name', 'nepali_name', 'slug', 'service_type',
            'is_featured', 'icon', 'color', 'description'
        )
        return context


class DigitalServiceDetailView(NepaliLanguageMixin, ServiceDetailViewMixin, DetailView):
    """Display details for a specific digital service."""
    model = DigitalService
    template_name = 'services/digital/digital_detail.html'
    context_object_name = 'service'
    service_type = 'digital'
    breadcrumbs = create_breadcrumbs(
        ('Home', '/'),
        ('Services', '/services/'),
        ('Digital Service', None)
    )
    
    def get_context_data(self, **kwargs):
        """Add related digital services to context."""
        context = super().get_context_data(**kwargs)
        # Get 3 random active digital services excluding the current one
        active_ids = list(
            DigitalService.objects.filter(is_active=True)
            .exclude(id=self.object.id)
            .values_list('id', flat=True)
        )
        
        if active_ids:
            random_ids = random.sample(active_ids, min(len(active_ids), 3))
            context['related_digital'] = DigitalService.objects.filter(
                id__in=random_ids
            ).only(
                'id', 'english_name', 'nepali_name', 'slug', 'service_type',
                'is_featured', 'icon', 'color', 'description', 'features'
            )
        else:
            context['related_digital'] = DigitalService.objects.none()
        
        return context


# Import base calculator view
from .calculator_views import BaseCalculatorView


class LoanCalculatorView(BaseCalculatorView):
    """Loan calculator view using base class pattern."""
    form_class = LoanCalculatorForm
    template_name = 'services/shared/loan_calculator.html'
    page_title = 'Loan Calculator'
    page_description = 'Calculate your loan EMI and total amount'
    calculator_type = 'loan'
    service_type = 'loan'
    
    def perform_calculation(self, form: Form) -> tuple[Dict[str, Any], Any]:
        """Perform loan EMI calculation."""
        loan_type = form.cleaned_data['loan_type']
        principal = form.cleaned_data['principal_amount']
        tenure_years = form.cleaned_data['tenure_years']
        payment_frequency = form.cleaned_data['payment_frequency']
        
        # Convert monthly interest rate to annual rate
        # FinancialCalculator.calculate_loan_emi expects annual_rate
        # It will handle quarterly conversion internally (dividing by 400 for quarterly, 1200 for monthly)
        annual_rate = loan_type.monthly_interest_rate * 12
        
        tenure_months = tenure_years * 12
        calculation = FinancialCalculator.calculate_loan_emi(
            principal, annual_rate, tenure_months, payment_frequency
        )
        
        return calculation, loan_type


class SavingsCalculatorView(BaseCalculatorView):
    """Savings calculator view using base class pattern."""
    form_class = SavingsCalculatorForm
    template_name = 'services/shared/savings_calculator.html'
    page_title = 'Savings Calculator'
    page_description = 'Calculate your savings maturity amount'
    calculator_type = 'savings'
    service_type = 'savings'
    
    def perform_calculation(self, form: Form) -> tuple[Dict[str, Any], Any]:
        """Perform savings maturity calculation."""
        savings_type = form.cleaned_data['savings_type']
        monthly_deposit = form.cleaned_data['monthly_deposit']
        tenure_years = form.cleaned_data['tenure_years']
        
        calculation = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit, savings_type.interest_rate, tenure_years
        )
        
        return calculation, savings_type


class FixedDepositCalculatorView(BaseCalculatorView):
    """Fixed deposit calculator view using base class pattern."""
    form_class = FixedDepositCalculatorForm
    template_name = 'services/shared/fixed_deposit_calculator.html'
    page_title = 'Fixed Deposit Calculator'
    page_description = 'Calculate your fixed deposit maturity amount'
    calculator_type = 'fixed_deposit'
    service_type = 'fixed_deposit'
    
    def perform_calculation(self, form: Form) -> tuple[Dict[str, Any], Any]:
        """Perform fixed deposit maturity calculation."""
        deposit_type = form.cleaned_data['deposit_type']
        deposit_amount = form.cleaned_data['deposit_amount']
        
        calculation = FinancialCalculator.calculate_fixed_deposit_maturity(
            deposit_amount, deposit_type.interest_rate, 
            deposit_type.duration_months, deposit_type.payment_frequency
        )
        
        return calculation, deposit_type


# Keep function-based views for backward compatibility (can be removed later)
loan_calculator = LoanCalculatorView.as_view()
savings_calculator = SavingsCalculatorView.as_view()
fixed_deposit_calculator = FixedDepositCalculatorView.as_view()


class ServiceApplicationView(NepaliLanguageMixin, FormView):
    """Service application form view."""
    template_name = 'services/shared/application.html'
    form_class = ServiceApplicationForm
    success_url = '/contact/thank-you/'  # Redirect to general thank you or specific one

    def get_initial(self):
        """Pre-fill form based on GET/POST parameters."""
        initial = super().get_initial()
        request = self.request
        service_type = request.GET.get('service_type', '') or request.POST.get('service_type', '')
        service_id = request.GET.get('service_id', '') or request.POST.get('service_id', '')
        service_slug = request.GET.get('service_slug', '')

        # Handle slug to ID conversion if needed
        if service_slug and not service_id:
            model_class = SERVICE_MODEL_MAPPING.get(service_type)
            if model_class:
                try:
                    obj = model_class.objects.filter(slug=service_slug).first()
                    if obj:
                        service_id = obj.id
                except Exception:
                    pass
        
        if service_type:
            initial['service_type'] = service_type
        if service_id:
            initial['service_id'] = service_id
            
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add service info to context for display
        initial = self.get_initial()
        service_type = initial.get('service_type')
        service_id = initial.get('service_id')
        
        if service_type and service_id:
            model_class = SERVICE_MODEL_MAPPING.get(service_type)
            if model_class:
                try:
                    service_obj = model_class.objects.filter(id=service_id).first()
                    if service_obj:
                        context['selected_service'] = service_obj
                        # Handle varied name fields (english_name vs name)
                        context['service_name'] = getattr(service_obj, 'english_name', str(service_obj))
                except Exception:
                    pass
                    
        return context

    def form_valid(self, form):
        # Process the form using service
        try:
            ServiceApplicationService.process_application(form.cleaned_data)
            messages.success(self.request, _('Your application has been submitted successfully.'))
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Error submitting application: {str(e)}")
            return self.form_invalid(form)


class ServiceComparisonView(NepaliLanguageMixin, FormView):
    """Compare services side by side."""
    template_name = 'services/shared/comparison.html'
    form_class = ServiceComparisonForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # If parameters provided, perform comparison
        request = self.request
        service_type = request.GET.get('service_type')
        service_ids = request.GET.getlist('service_ids')
        
        if service_type and service_ids:
            try:
                comparison_data = ServiceComparisonService.compare_services(service_type, service_ids)
                context['comparison_data'] = comparison_data
                context['service_type'] = service_type
                
                # Pre-fill form
                form = self.get_form()
                form.initial['service_type'] = service_type
                # Note: Setting initial for multiple checkboxes might need handling in form init
                context['form'] = form
                
            except Exception as e:
                messages.error(request, f"Error comparing services: {str(e)}")
                
        return context

    def form_valid(self, form):
        """Handle form submission by redirecting to GET URL."""
        from django.http import QueryDict
        from django.shortcuts import redirect
        
        service_type = form.cleaned_data['service_type']
        service_ids = form.cleaned_data['services']
        
        q = QueryDict(mutable=True)
        q['service_type'] = service_type
        q.setlist('service_ids', service_ids)
        
        return redirect(f"{self.request.path}?{q.urlencode()}")


class ServiceSearchView(NepaliLanguageMixin, FormView):
    """Search for services based on criteria."""
    template_name = 'services/shared/search.html'
    form_class = ServiceSearchForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        
        if query or category:
            results = ServiceSearchService.search_services(query, category)
            context['results'] = results
            context['query'] = query
            context['category'] = category
            
            # Update form initial
            form = self.get_form()
            form.initial['query'] = query
            form.initial['category'] = category
            context['form'] = form
            
        return context


class CalculatorAPIView(APIView):
    """API endpoint for all financial calculators."""
    
    def post(self, request, *args, **kwargs):
        try:
            data, error_response = safe_json_parse(request)
            if error_response:
                return error_response
            
            calculator_type = data.get('type')
            
            result = None
            
            if calculator_type == 'loan':
                principal, err = safe_float_conversion(data.get('principal', 0), field_name='principal')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                interest_rate, err = safe_float_conversion(data.get('interest_rate', 0), field_name='interest_rate')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                tenure_months, err = safe_int_conversion(data.get('tenure_months', 0), field_name='tenure_months')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                payment_frequency = data.get('payment_frequency', 'monthly')
                
                if principal <= 0 or interest_rate < 0 or tenure_months <= 0:
                     return Response({'error': 'Invalid input: principal, interest_rate, and tenure_months must be positive', 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                result = FinancialCalculator.calculate_loan_emi(
                    principal, interest_rate, tenure_months, payment_frequency
                )
                
            elif calculator_type == 'savings':
                monthly_deposit, err = safe_float_conversion(data.get('monthly_deposit', 0), field_name='monthly_deposit')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                interest_rate, err = safe_float_conversion(data.get('interest_rate', 0), field_name='interest_rate')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                tenure_years, err = safe_int_conversion(data.get('tenure_years', 0), field_name='tenure_years')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                if monthly_deposit <= 0 or interest_rate < 0 or tenure_years <= 0:
                    return Response({'error': 'Invalid input values', 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                result = FinancialCalculator.calculate_savings_maturity(
                    monthly_deposit, interest_rate, tenure_years
                )
                
            elif calculator_type == 'fixed_deposit':
                principal, err = safe_float_conversion(data.get('principal', 0), field_name='principal')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                interest_rate, err = safe_float_conversion(data.get('interest_rate', 0), field_name='interest_rate')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                tenure_months, err = safe_int_conversion(data.get('tenure_months', 0), field_name='tenure_months')
                if err:
                    return Response({'error': err, 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                payment_frequency = data.get('payment_frequency', 'lump_sum')
                
                if principal <= 0 or interest_rate < 0 or tenure_months <= 0:
                    return Response({'error': 'Invalid input values', 'code': 'INVALID_INPUT'}, status=status.HTTP_400_BAD_REQUEST)
                
                result = FinancialCalculator.calculate_fixed_deposit_maturity(
                    principal, interest_rate, tenure_months, payment_frequency
                )
            else:
                return Response({'error': f'Invalid calculator type: {calculator_type}', 'code': 'INVALID_CALCULATOR_TYPE'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Calculation successful', 'data': {'result': result}})
            
        except ValueError as e:
            ErrorLogger.log_error(e, request, level='warning')
            return Response({'error': str(e), 'code': 'CALCULATION_ERROR'}, status=status.HTTP_400_BAD_REQUEST)


class ServiceOptionsAPIView(View):
    """
    API endpoint to fetch available services for a given type.
    Used by the comparison tool's frontend.
    """
    def get(self, request, *args, **kwargs):
        service_type = request.GET.get('service_type')
        if not service_type:
            return JsonResponse({'error': 'service_type is required'}, status=400)
            
        data = []
        if service_type == 'savings':
            services = SavingsAccount.objects.filter(is_active=True).order_by('english_name')
            data = [{'id': s.id, 'name': s.english_name} for s in services]
        elif service_type == 'loans':
            services = LoanType.objects.filter(is_active=True).order_by('english_name')
            data = [{'id': s.id, 'name': s.english_name} for s in services]
        elif service_type == 'fixed_deposits':
            services = FixedDeposit.objects.filter(is_active=True).order_by('duration_months')
            # Use display methods for user-friendly names
            data = [{'id': s.id, 'name': f"{s.get_duration_months_display()} - {s.get_payment_frequency_display()}"} for s in services]
        else:
            return JsonResponse({'error': 'Invalid service_type'}, status=400)
            
        return JsonResponse({'services': data})

# Mapping for URL compatibility
service_application = ServiceApplicationView.as_view()
service_comparison = ServiceComparisonView.as_view()
service_search = ServiceSearchView.as_view()
calculator_api = CalculatorAPIView.as_view()
service_options_api = ServiceOptionsAPIView.as_view()
