from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.paginator import Paginator
import json
from datetime import date, datetime
from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, MemberRelief,
    ServiceApplication, ServiceAnalytics, ServiceRecommendation
)
from .forms import (
    LoanCalculatorForm, SavingsCalculatorForm, FixedDepositCalculatorForm,
    ServiceApplicationForm, ServiceComparisonForm, ServiceSearchForm, ServiceRecommendationForm
)
from .utils import FinancialCalculator, ServiceRecommendationEngine, ServiceComparison


def services_overview(request):
    """Main services overview page"""
    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Services', 'url': '/services/'}
    ]
    
    recommendation_form = ServiceRecommendationForm()
    recommendations = None

    if request.method == 'POST':
        recommendation_form = ServiceRecommendationForm(request.POST)
        if recommendation_form.is_valid():
            user_profile = recommendation_form.cleaned_data
            recommendations = ServiceRecommendationEngine.get_recommendations(user_profile)
            
            # Save the recommendation for analytics
            ServiceRecommendation.objects.create(
                user_profile=user_profile,
                recommended_services=recommendations,
                recommendation_reason='\n'.join(recommendations['reasoning']),
                confidence_score=0.9  # Placeholder confidence
            )

    context = {
        'savings_accounts': SavingsAccount.objects.filter(is_active=True),
        'fixed_deposits': FixedDeposit.objects.filter(is_active=True),
        'loan_types': LoanType.objects.filter(is_active=True),
        'remittance_services': RemittanceService.objects.filter(is_active=True),
        'member_reliefs': MemberRelief.objects.filter(is_active=True),
        'featured_savings': SavingsAccount.objects.filter(is_active=True, is_featured=True)[:3],
        'featured_loans': LoanType.objects.filter(is_active=True, is_featured=True)[:3],
        'breadcrumbs': breadcrumbs,
        'recommendation_form': recommendation_form,
        'recommendations': recommendations,
    }
    return render(request, 'services/services.html', context)


class SavingsAccountsView(ListView):
    """Display all savings account types"""
    model = SavingsAccount
    template_name = 'services/savings/list.html'
    context_object_name = 'savings_accounts'
    
    def get_queryset(self):
        return SavingsAccount.objects.filter(is_active=True).order_by('-is_featured', 'interest_rate', 'account_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Savings Accounts'
        context['page_description'] = 'Choose from our range of savings accounts with competitive interest rates'
        context['featured_accounts'] = SavingsAccount.objects.filter(is_active=True, is_featured=True)
        return context


class FixedDepositsView(ListView):
    """Display all fixed deposit options"""
    model = FixedDeposit
    template_name = 'services/fixed_deposit/list.html'
    context_object_name = 'fixed_deposits'
    
    def get_queryset(self):
        return FixedDeposit.objects.filter(is_active=True).order_by('duration_months', 'payment_frequency')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fixed Deposits'
        context['page_description'] = 'Secure your future with our fixed deposit schemes'
        
        # Group by duration for better display
        deposits_by_duration = {}
        for deposit in context['fixed_deposits']:
            duration = deposit.get_duration_months_display()
            if duration not in deposits_by_duration:
                deposits_by_duration[duration] = []
            deposits_by_duration[duration].append(deposit)
        
        context['deposits_by_duration'] = deposits_by_duration
        return context


class LoanServicesView(ListView):
    """Display all loan services"""
    model = LoanType
    template_name = 'services/loan/list.html'
    context_object_name = 'loan_types'
    
    def get_queryset(self):
        return LoanType.objects.filter(is_active=True).order_by('-is_featured', 'loan_category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Loan Services'
        context['page_description'] = 'Flexible loan options for all your financial needs'
        context['featured_loans'] = LoanType.objects.filter(is_active=True, is_featured=True)
        return context


class RemittanceServicesView(ListView):
    """Display remittance services"""
    model = RemittanceService
    template_name = 'services/remittance/list.html'
    context_object_name = 'remittance_services'
    
    def get_queryset(self):
        return RemittanceService.objects.filter(is_active=True).order_by('service_type')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remittance Services'
        context['page_description'] = 'Fast and secure money transfer services'
        return context


class MemberReliefView(ListView):
    """Display member relief programs"""
    model = MemberRelief
    template_name = 'services/member_relief/list.html'
    context_object_name = 'member_reliefs'
    
    def get_queryset(self):
        return MemberRelief.objects.filter(is_active=True).order_by('relief_type', 'title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Member Relief Programs'
        context['page_description'] = 'Support and assistance programs for our valued members'
        
        # Group by relief type
        reliefs_by_type = {}
        for relief in context['member_reliefs']:
            relief_type = relief.get_relief_type_display()
            if relief_type not in reliefs_by_type:
                reliefs_by_type[relief_type] = []
            reliefs_by_type[relief_type].append(relief)
        
        context['reliefs_by_type'] = reliefs_by_type
        return context


# --- Detail Views (UPGRADED to Class-Based Views with Slugs) ---

class SavingsDetailView(DetailView):
    """Display details for a specific savings account."""
    model = SavingsAccount
    template_name = 'services/savings/detail.html'
    context_object_name = 'service'

class LoanDetailView(DetailView):
    """Display details for a specific loan type."""
    model = LoanType
    template_name = 'services/loan/detail.html'
    context_object_name = 'service'

class FixedDepositDetailView(DetailView):
    """Display details for a specific fixed deposit scheme."""
    model = FixedDeposit
    template_name = 'services/fixed_deposit/detail.html'
    context_object_name = 'service'

class RemittanceDetailView(DetailView):
    """Display details for a specific remittance service."""
    model = RemittanceService
    template_name = 'services/remittance/detail.html'
    context_object_name = 'service'

class MemberReliefDetailView(DetailView):
    """Display details for a specific member relief program."""
    model = MemberRelief
    template_name = 'services/member_relief/detail.html'
    context_object_name = 'service'


def loan_calculator(request):
    """Loan calculator view"""
    if request.method == 'POST':
        form = LoanCalculatorForm(request.POST)
        if form.is_valid():
            loan_type = form.cleaned_data['loan_type']
            principal = form.cleaned_data['principal_amount']
            tenure_years = form.cleaned_data['tenure_years']
            payment_frequency = form.cleaned_data['payment_frequency']
            
            # Get interest rate based on payment frequency
            if payment_frequency == 'monthly':
                interest_rate = loan_type.monthly_interest_rate
            else:
                interest_rate = loan_type.quarterly_installment_rate
            
            tenure_months = tenure_years * 12
            calculation = FinancialCalculator.calculate_loan_emi(
                principal, interest_rate, tenure_months, payment_frequency
            )
            
            # Track calculator usage
            ServiceAnalytics.objects.update_or_create(
                service_type='loan',
                service_id=loan_type.id,
                date=date.today(),
                defaults={'calculator_usage': 1}
            )
            
            context = {
                'form': form,
                'calculation': calculation,
                'loan_type': loan_type,
                'page_title': 'Loan Calculator',
                'page_description': 'Calculate your loan EMI and total amount'
            }
            return render(request, 'services/shared/loan_calculator.html', context)
    else:
        form = LoanCalculatorForm()
    
    context = {
        'form': form,
        'page_title': 'Loan Calculator',
        'page_description': 'Calculate your loan EMI and total amount'
    }
    return render(request, 'services/shared/loan_calculator.html', context)


def savings_calculator(request):
    """Savings calculator view"""
    if request.method == 'POST':
        form = SavingsCalculatorForm(request.POST)
        if form.is_valid():
            savings_type = form.cleaned_data['savings_type']
            monthly_deposit = form.cleaned_data['monthly_deposit']
            tenure_years = form.cleaned_data['tenure_years']
            
            calculation = FinancialCalculator.calculate_savings_maturity(
                monthly_deposit, savings_type.interest_rate, tenure_years
            )
            
            # Track calculator usage
            ServiceAnalytics.objects.update_or_create(
                service_type='savings',
                service_id=savings_type.id,
                date=date.today(),
                defaults={'calculator_usage': 1}
            )
            
            context = {
                'form': form,
                'calculation': calculation,
                'savings_type': savings_type,
                'page_title': 'Savings Calculator',
                'page_description': 'Calculate your savings maturity amount'
            }
            return render(request, 'services/shared/savings_calculator.html', context)
    else:
        form = SavingsCalculatorForm()
    
    context = {
        'form': form,
        'page_title': 'Savings Calculator',
        'page_description': 'Calculate your savings maturity amount'
    }
    return render(request, 'services/shared/savings_calculator.html', context)


def fixed_deposit_calculator(request):
    """Fixed deposit calculator view"""
    if request.method == 'POST':
        form = FixedDepositCalculatorForm(request.POST)
        if form.is_valid():
            deposit_type = form.cleaned_data['deposit_type']
            deposit_amount = form.cleaned_data['deposit_amount']
            
            calculation = FinancialCalculator.calculate_fixed_deposit_maturity(
                deposit_amount, deposit_type.interest_rate, 
                deposit_type.duration_months, deposit_type.payment_frequency
            )
            
            # Track calculator usage
            ServiceAnalytics.objects.update_or_create(
                service_type='fixed_deposit',
                service_id=deposit_type.id,
                date=date.today(),
                defaults={'calculator_usage': 1}
            )
            
            context = {
                'form': form,
                'calculation': calculation,
                'deposit_type': deposit_type,
                'page_title': 'Fixed Deposit Calculator',
                'page_description': 'Calculate your fixed deposit maturity amount'
            }
            return render(request, 'services/shared/fixed_deposit_calculator.html', context)
    else:
        form = FixedDepositCalculatorForm()
    
    context = {
        'form': form,
        'page_title': 'Fixed Deposit Calculator',
        'page_description': 'Calculate your fixed deposit maturity amount'
    }
    return render(request, 'services/shared/fixed_deposit_calculator.html', context)


def service_application(request):
    """Service application form view"""
    if request.method == 'POST':
        form = ServiceApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.application_data = {
                'service_type': form.cleaned_data['service_type'],
                'service_id': form.cleaned_data['service_id'],
                'additional_info': form.cleaned_data['additional_info']
            }
            application.save()
            
            # Track application
            ServiceAnalytics.objects.update_or_create(
                service_type=application.service_type,
                service_id=application.service_id,
                date=date.today(),
                defaults={'applications_received': 1}
            )
            
            messages.success(request, 'Your application has been submitted successfully! We will contact you soon.')
            return redirect('services:overview')
    else:
        # Pre-fill form if coming from service detail page
        service_type = request.GET.get('service_type', '')
        service_id = request.GET.get('service_id', '')
        service_slug = request.GET.get('service_slug', '')
        
        # If service_slug is provided, convert it to service_id
        if service_slug and not service_id:
            try:
                if service_type == 'savings':
                    service = SavingsAccount.objects.get(slug=service_slug)
                elif service_type == 'loan':
                    service = LoanType.objects.get(slug=service_slug)
                elif service_type == 'fixed_deposit':
                    service = FixedDeposit.objects.get(slug=service_slug)
                elif service_type == 'remittance':
                    service = RemittanceService.objects.get(slug=service_slug)
                elif service_type == 'relief':
                    service = MemberRelief.objects.get(slug=service_slug)
                else:
                    service = None
                
                if service:
                    service_id = str(service.id)
            except:
                service_id = ''
        
        form = ServiceApplicationForm(initial={
            'service_type': service_type,
            'service_id': service_id
        })
    
    context = {
        'form': form,
        'page_title': 'Service Application',
        'page_description': 'Apply for our financial services'
    }
    return render(request, 'services/shared/application.html', context)


def service_comparison(request):
    """Service comparison view"""
    if request.method == 'POST':
        form = ServiceComparisonForm(request.POST)
        if form.is_valid():
            service_type = form.cleaned_data['service_type']
            service_ids = form.cleaned_data['services']
            
            if service_type == 'savings':
                comparison_data = ServiceComparison.compare_savings_accounts(service_ids)
                template = 'services/savings_comparison.html'
            elif service_type == 'loans':
                comparison_data = ServiceComparison.compare_loans(service_ids)
                template = 'services/loans_comparison.html'
            elif service_type == 'fixed_deposits':
                comparison_data = ServiceComparison.compare_fixed_deposits(service_ids)
                template = 'services/fixed_deposits_comparison.html'
            else:
                messages.error(request, 'Invalid service type selected.')
                return redirect('services:comparison')
            
            # Track comparison views
            for service_id in service_ids:
                ServiceAnalytics.objects.update_or_create(
                    service_type=service_type,
                    service_id=service_id,
                    date=date.today(),
                    defaults={'comparison_views': 1}
                )
            
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
    form = ServiceSearchForm(request.GET)
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        service_type = form.cleaned_data.get('service_type', '')
        interest_rate_min = form.cleaned_data.get('interest_rate_min')
        interest_rate_max = form.cleaned_data.get('interest_rate_max')
        featured_only = form.cleaned_data.get('featured_only', False)
        
        # Build search queries
        if service_type == 'savings' or not service_type:
            savings_q = Q(is_active=True)
            if query:
                savings_q &= (Q(english_name__icontains=query) | Q(nepali_name__icontains=query) | 
                            Q(description__icontains=query))
            if interest_rate_min:
                savings_q &= Q(interest_rate__gte=interest_rate_min)
            if interest_rate_max:
                savings_q &= Q(interest_rate__lte=interest_rate_max)
            if featured_only:
                savings_q &= Q(is_featured=True)
            
            savings_results = SavingsAccount.objects.filter(savings_q)
            for account in savings_results:
                results.append({
                    'type': 'savings',
                    'id': account.id,
                    'name': account.english_name,
                    'nepali_name': account.nepali_name,
                    'interest_rate': account.interest_rate,
                    'description': account.description,
                    'url': f'/services/savings/{account.id}/',
                    'icon': account.icon,
                    'color': account.color
                })
        
        if service_type == 'loans' or not service_type:
            loans_q = Q(is_active=True)
            if query:
                loans_q &= (Q(english_name__icontains=query) | Q(nepali_name__icontains=query) | 
                           Q(description__icontains=query))
            if interest_rate_min:
                loans_q &= Q(monthly_interest_rate__gte=interest_rate_min)
            if interest_rate_max:
                loans_q &= Q(monthly_interest_rate__lte=interest_rate_max)
            if featured_only:
                loans_q &= Q(is_featured=True)
            
            loans_results = LoanType.objects.filter(loans_q)
            for loan in loans_results:
                results.append({
                    'type': 'loan',
                    'id': loan.id,
                    'name': loan.english_name,
                    'nepali_name': loan.nepali_name,
                    'interest_rate': loan.monthly_interest_rate,
                    'description': loan.description,
                    'url': f'/services/loans/{loan.id}/',
                    'icon': loan.icon,
                    'color': loan.color
                })
    
    # Paginate results
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'results': page_obj,
        'total_results': len(results),
        'page_title': 'Service Search',
        'page_description': 'Find the perfect financial service for your needs'
    }
    return render(request, 'services/shared/search.html', context)


def service_recommendations(request):
    """Service recommendations based on user profile"""
    if request.method == 'POST':
        user_profile = {
            'age': int(request.POST.get('age', 30)),
            'monthly_income': int(request.POST.get('monthly_income', 50000)),
            'goals': request.POST.getlist('goals'),
            'risk_tolerance': request.POST.get('risk_tolerance', 'moderate')
        }
        
        recommendations = ServiceRecommendationEngine.get_recommendations(user_profile)
        
        # Save recommendation
        ServiceRecommendation.objects.create(
            user_profile=user_profile,
            recommended_services=recommendations,
            recommendation_reason='\n'.join(recommendations['reasoning']),
            confidence_score=85.0  # Placeholder confidence score
        )
        
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


@csrf_exempt
def calculator_api(request):
    """API endpoint for calculator calculations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            calculator_type = data.get('type')
            
            if calculator_type == 'loan':
                principal = float(data.get('principal', 0))
                interest_rate = float(data.get('interest_rate', 0))
                tenure_months = int(data.get('tenure_months', 0))
                payment_frequency = data.get('payment_frequency', 'monthly')
                
                result = FinancialCalculator.calculate_loan_emi(
                    principal, interest_rate, tenure_months, payment_frequency
                )
                
            elif calculator_type == 'savings':
                monthly_deposit = float(data.get('monthly_deposit', 0))
                interest_rate = float(data.get('interest_rate', 0))
                tenure_years = int(data.get('tenure_years', 0))
                
                result = FinancialCalculator.calculate_savings_maturity(
                    monthly_deposit, interest_rate, tenure_years
                )
                
            elif calculator_type == 'fixed_deposit':
                principal = float(data.get('principal', 0))
                interest_rate = float(data.get('interest_rate', 0))
                tenure_months = int(data.get('tenure_months', 0))
                payment_frequency = data.get('payment_frequency', 'lump_sum')
                
                result = FinancialCalculator.calculate_fixed_deposit_maturity(
                    principal, interest_rate, tenure_months, payment_frequency
                )
            else:
                return JsonResponse({'error': 'Invalid calculator type'}, status=400)
            
            return JsonResponse({'success': True, 'result': result})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
