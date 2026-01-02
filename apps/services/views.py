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
        
        # Get all active savings accounts
        all_savings = SavingsAccount.objects.filter(is_active=True).order_by('category', '-interest_rate')
        
        # Group by category
        context['regular_savings'] = all_savings.filter(category='regular')
        context['optional_savings'] = all_savings.filter(category='optional')
        context['recurring_savings'] = all_savings.filter(category='recurring')
        
        # Periodic Savings (Fixed Deposits)
        context['periodic_savings'] = FixedDeposit.objects.filter(is_active=True).order_by('duration_months')
        
        context['featured_accounts'] = all_savings.filter(is_featured=True).only(
            'id', 'english_name', 'nepali_name', 'slug', 'account_type', 
            'interest_rate', 'is_featured', 'icon', 'color'
        )
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
        ).order_by('service_type', 'english_name')
    
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
        
        # Group remittances by service type
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
        return MemberRelief.objects.filter(is_active=True).order_by('relief_type', 'english_name')
    
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


class DigitalServicesView(NepaliLanguageMixin, ListView):
    """Display digital services"""
    model = DigitalService
    template_name = 'services/digital/digital_list.html'
    context_object_name = 'digital_services'
    
    def get_queryset(self):
        return DigitalService.objects.filter(is_active=True).order_by('service_type', 'english_name')
    
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
        
        # Get interest rate based on payment frequency
        interest_rate = loan_type.monthly_interest_rate
        if payment_frequency != 'monthly':
            # For quarterly, use monthly rate (simplified)
            interest_rate = loan_type.monthly_interest_rate
        
        tenure_months = tenure_years * 12
        calculation = FinancialCalculator.calculate_loan_emi(
            principal, interest_rate, tenure_months, payment_frequency
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


def service_application(request):
    """Service application form view"""
    activate('ne')
    # Get service info from GET params (for pre-filling) or POST data
    service_type = request.GET.get('service_type', '') or request.POST.get('service_type', '')
    service_id = request.GET.get('service_id', '') or request.POST.get('service_id', '')
    service_slug = request.GET.get('service_slug', '')
    
    # If service_slug is provided, convert it to service_id
    if service_slug and not service_id:
        model_class = SERVICE_MODEL_MAPPING.get(service_type)
        if model_class:
            try:
                # FixedDeposit uses ID as slug in the logic, others use slug field
                if service_type == 'fixed_deposit':
                    service = model_class.objects.get(id=int(service_slug))
                else:
                    service = model_class.objects.get(slug=service_slug)
                service_id = str(service.id)
            except (ValueError, model_class.DoesNotExist):
                service_id = ''
        else:
            service_id = ''
    
    # Get service object for form
    service_object = None
    if service_type and service_id:
        model_class = SERVICE_MODEL_MAPPING.get(service_type)
        if model_class:
            try:
                service_object = model_class.objects.get(id=int(service_id))
            except (ValueError, model_class.DoesNotExist):
                service_object = None
    
    if request.method == 'POST':
        form = ServiceApplicationForm(request.POST, service_object=service_object)
        if form.is_valid():
            # Get service_type and service_id from form or request
            form_service_type = form.cleaned_data.get('service_type') or service_type
            form_service_id = form.cleaned_data.get('service_id') or service_id
            if form_service_type and form_service_id:
                ServiceApplicationService.process_application(form, form_service_type, form_service_id)
                messages.success(request, _('तपाईंको आवेदन सफलतापूर्वक पेश गरियो! हामी छिट्टै सम्पर्क गर्नेछौं।'))
                return redirect('services:overview')
            else:
                messages.error(request, _('सेवा जानकारी हराइरहेको छ। कृपया पहिले सेवा छान्नुहोस्।'))
    else:
        form = ServiceApplicationForm(service_object=service_object, initial={
            'service_type': service_type,
            'service_id': service_id
        })
    
    context = {
        'form': form,
        'service_type': service_type,
        'service_id': service_id,
        'page_title': 'Service Application',
        'page_description': 'Apply for our financial services'
    }
    return render(request, 'services/shared/application.html', context)


def service_comparison(request):
    """Service comparison view"""
    activate('ne')
    if request.method == 'POST':
        form = ServiceComparisonForm(request.POST)
        if form.is_valid():
            service_type = form.cleaned_data['service_type']
            service_ids = form.cleaned_data['services']
            
            if service_type == 'savings':
                comparison_data = ServiceComparisonService.compare_savings_accounts(service_ids)
                template = 'services/savings_comparison.html'
            elif service_type == 'loans':
                comparison_data = ServiceComparisonService.compare_loans(service_ids)
                template = 'services/loans_comparison.html'
            elif service_type == 'fixed_deposits':
                comparison_data = ServiceComparisonService.compare_fixed_deposits(service_ids)
                template = 'services/fixed_deposits_comparison.html'
            else:
                messages.error(request, _('अवैध सेवा प्रकार छानिएको छ।'))
                return redirect('services:service_comparison')
            
            # Track comparison views
            for service_id in service_ids:
                ServiceAnalyticsService.track_usage(service_type, service_id, 'comparison_views')
            
            context = {
                'form': form,
                'comparison_data': comparison_data,
                'service_type': service_type,
                'page_title': f'{service_type.title()} Comparison',
                'page_description': f'Compare {service_type} options'
            }
            return render(request, template, context)
    else:
        form = ServiceComparisonForm()
    
    context = {
        'form': form,
        'page_title': 'Service Comparison',
        'page_description': 'Compare different service options'
    }
    return render(request, 'services/shared/comparison.html', context)

def service_search(request):
    """Enhanced service search view"""
    activate('ne')
    form = ServiceSearchForm(request.GET)
    page = request.GET.get('page', 1)
    
    # Use cleaned data if valid, else empty? Or raw GET?
    # View usually validates form first.
    data = {}
    if form.is_valid():
        data = form.cleaned_data
    else:
        # If invalid (e.g. empty) we might still want default results? 
        # But form.cleaned_data is only available if valid.
        # Fallback to GET params or just empty.
        pass

    results_data = ServiceSearchService.search_services(data, page_number=page)
    
    context = {
        'form': form,
        'results': results_data['results'],
        'total_results': results_data['total_results'],
        'page_title': 'Service Search',
        'page_description': 'Find the perfect financial service for your needs'
    }
    return render(request, 'services/shared/search.html', context)


def service_recommendations(request):
    """Service recommendations based on user profile"""
    activate('ne')
    if request.method == 'POST':
        user_profile = {
            'age': int(request.POST.get('age', 30)),
            'monthly_income': int(request.POST.get('monthly_income', 50000)),
            'goals': request.POST.getlist('goals'),
            'risk_tolerance': request.POST.get('risk_tolerance', 'moderate')
        }
        
        recommendations = ServiceRecommendationService.get_recommendations(user_profile)
        ServiceRecommendationService.save_recommendation(user_profile, recommendations)
        
        context = {
            'user_profile': user_profile,
            'recommendations': recommendations,
            'page_title': 'Service Recommendations',
            'page_description': 'Personalized service recommendations for you'
        }
        return render(request, 'services/service_recommendations.html', context)
    
    context = {
        'page_title': 'Service Recommendations',
        'page_description': 'Get personalized service recommendations'
    }
    return render(request, 'services/service_recommendation_form.html', context)


from apps.core.error_handling import (
    ErrorResponse, ErrorLogger, handle_api_errors, safe_json_parse,
    safe_float_conversion, safe_int_conversion
)

@csrf_exempt
@handle_api_errors
def calculator_api(request):
    """API endpoint for calculator calculations"""
    activate('ne')
    if request.method != 'POST':
        return ErrorResponse.json_error(
            message='Method not allowed',
            status_code=405,
            error_code='METHOD_NOT_ALLOWED'
        )
    
    # Parse JSON safely
    data, error_response = safe_json_parse(request)
    if error_response:
        return error_response
    
    calculator_type = data.get('type')
    if not calculator_type:
        return ErrorResponse.json_error(
            message='Missing calculator type',
            status_code=400,
            error_code='MISSING_TYPE'
        )
    
    result = None
    
    try:
        if calculator_type == 'loan':
            principal, err = safe_float_conversion(data.get('principal', 0), field_name='principal')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            interest_rate, err = safe_float_conversion(data.get('interest_rate', 0), field_name='interest_rate')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            tenure_months, err = safe_int_conversion(data.get('tenure_months', 0), field_name='tenure_months')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            payment_frequency = data.get('payment_frequency', 'monthly')
            
            if principal <= 0 or interest_rate < 0 or tenure_months <= 0:
                return ErrorResponse.json_error(
                    message='Invalid input: principal, interest_rate, and tenure_months must be positive',
                    status_code=400,
                    error_code='INVALID_INPUT'
                )
            
            result = FinancialCalculator.calculate_loan_emi(
                principal, interest_rate, tenure_months, payment_frequency
            )
            
        elif calculator_type == 'savings':
            monthly_deposit, err = safe_float_conversion(data.get('monthly_deposit', 0), field_name='monthly_deposit')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            interest_rate, err = safe_float_conversion(data.get('interest_rate', 0), field_name='interest_rate')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            tenure_years, err = safe_int_conversion(data.get('tenure_years', 0), field_name='tenure_years')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            if monthly_deposit <= 0 or interest_rate < 0 or tenure_years <= 0:
                return ErrorResponse.json_error(
                    message='Invalid input: monthly_deposit, interest_rate, and tenure_years must be positive',
                    status_code=400,
                    error_code='INVALID_INPUT'
                )
            
            result = FinancialCalculator.calculate_savings_maturity(
                monthly_deposit, interest_rate, tenure_years
            )
            
        elif calculator_type == 'fixed_deposit':
            principal, err = safe_float_conversion(data.get('principal', 0), field_name='principal')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            interest_rate, err = safe_float_conversion(data.get('interest_rate', 0), field_name='interest_rate')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            tenure_months, err = safe_int_conversion(data.get('tenure_months', 0), field_name='tenure_months')
            if err:
                return ErrorResponse.json_error(message=err, status_code=400, error_code='INVALID_INPUT')
            
            payment_frequency = data.get('payment_frequency', 'lump_sum')
            
            if principal <= 0 or interest_rate < 0 or tenure_months <= 0:
                return ErrorResponse.json_error(
                    message='Invalid input: principal, interest_rate, and tenure_months must be positive',
                    status_code=400,
                    error_code='INVALID_INPUT'
                )
            
            result = FinancialCalculator.calculate_fixed_deposit_maturity(
                principal, interest_rate, tenure_months, payment_frequency
            )
        else:
            return ErrorResponse.json_error(
                message=f'Invalid calculator type: {calculator_type}',
                status_code=400,
                error_code='INVALID_CALCULATOR_TYPE'
            )
        
        return ErrorResponse.json_success(
            message='Calculation successful',
            data={'result': result}
        )
        
    except ValueError as e:
        ErrorLogger.log_error(e, request, level='warning')
        return ErrorResponse.json_error(
            message=str(e),
            status_code=400,
            error_code='CALCULATION_ERROR'
        )
