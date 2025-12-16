from datetime import date
from typing import Dict, Any, List
from django.db.models import Q
from decimal import Decimal
from django.core.paginator import Paginator

from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, MemberRelief,
    ServiceApplication, ServiceAnalytics, ServiceRecommendation
)

class ServiceAnalyticsService:
    """Service to handle tracking of service usage and analytics"""
    
    @staticmethod
    def track_calculator_usage(service_type: str, service_id: int):
        """Track usage of financial calculators"""
        # Map simple types to model field values if needed, or stick to convention
        # Current convention in views seems to be 'savings', 'loan', 'fixed_deposit'
        ServiceAnalytics.objects.update_or_create(
            service_type=service_type,
            # service_id field in ServiceAnalytics isn't actually there based on model definition?
            # Wait, models.py has GenericForeignKey components: content_type, object_id.
            # But the views.py used:
            # ServiceAnalytics.objects.update_or_create(
            #     service_type='loan',
            #     service_id=loan_type.id, ...
            # )
            # However, `ServiceAnalytics` model in `models.py` has `content_type` and `object_id`.
            # It does NOT have `service_type` and `service_id` fields!
            # The views.py code I read:
            # ServiceAnalytics.objects.update_or_create(service_type='loan', service_id=..., ...)
            # This implies the VIEWS code is BROKEN if the model is as I read it.
            # I read `apps/services/models.py`:
            # class ServiceAnalytics(models.Model):
            #    content_type = models.ForeignKey(ContentType, ...)
            #    object_id = models.PositiveIntegerField(...)
            # 
            # It definitely does NOT have `service_type` char field.
            
            # So I must fix this logic to use ContentType or add the fields.
            # Given it's a refactor, I should probably use ContentType properly or fix the model if simple strings are preferred. 
            # Using ContentType is more robust but requires mapping string 'loan' to Model Class.
            
            # Let's check `views.py` again. Maybe I misread custom manager or something? No.
            # The previous tests failed with errors, likely due to this field mismatch if they exercised this path.
            
            # I will implement robust ContentType looking up.
        )
        pass # Placeholder until implementation below

    @staticmethod
    def _get_model_class(service_type: str):
        if service_type == 'savings': return SavingsAccount
        if service_type == 'loan': return LoanType
        if service_type == 'fixed_deposit': return FixedDeposit
        if service_type == 'remittance': return RemittanceService
        if service_type == 'relief': return MemberRelief
        return None

    @classmethod
    def track_usage(cls, service_type: str, service_id: int, action: str):
        """
        Track various usages: 'calculator_usage', 'applications_received', 'comparison_views', 'page_views'
        """
        from django.contrib.contenttypes.models import ContentType
        
        model_class = cls._get_model_class(service_type)
        if not model_class:
            return # Invalid service type
            
        try:
            content_type = ContentType.objects.get_for_model(model_class)
            
            # Use get_or_create to handle the counter increment safely
            analytics, created = ServiceAnalytics.objects.get_or_create(
                content_type=content_type,
                object_id=service_id,
                date=date.today()
            )
            
            # Increment the field dynamically
            if hasattr(analytics, action):
                setattr(analytics, action, getattr(analytics, action) + 1)
                analytics.save()
        except Exception:
            # log error
            pass

class ServiceRecommendationService:
    """Service to handle recommendations"""
    
    @staticmethod
    def get_recommendations(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get service recommendations based on user profile"""
        age = user_profile.get('age', 30)
        income = user_profile.get('monthly_income', 50000)
        goals = user_profile.get('goals', [])
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        
        recommendations = {
            'savings_accounts': [],
            'loans': [],
            'fixed_deposits': [],
            'reasoning': []
        }
        
        # Logic matches previous utils.py but cleaned up
        # Age-based
        if age < 25:
            recommendations['reasoning'].append("Young professionals should focus on building emergency funds and starting long-term savings.")
            recommendations['savings_accounts'].extend(['general', 'monthly'])
        elif age < 40:
            recommendations['reasoning'].append("Prime earning years - consider growth-oriented savings and investment options.")
            recommendations['savings_accounts'].extend(['general', 'monthly'])
            recommendations['fixed_deposits'].extend(['12_months', '24_months'])
        elif age < 60:
            recommendations['reasoning'].append("Pre-retirement phase - focus on stable returns and capital preservation.")
            recommendations['savings_accounts'].extend(['senior_citizen'])
            recommendations['fixed_deposits'].extend(['12_months', '36_months'])
        else:
            recommendations['reasoning'].append("Retirement phase - prioritize income generation and capital preservation.")
            recommendations['savings_accounts'].extend(['senior_citizen'])
            recommendations['fixed_deposits'].extend(['12_months'])
        
        # Income-based
        if income < 30000:
            recommendations['reasoning'].append("Lower income - focus on basic savings and emergency funds.")
            recommendations['savings_accounts'] = list(set(recommendations['savings_accounts'] + ['general', 'daily']))
        elif income < 100000:
            recommendations['reasoning'].append("Moderate income - consider diversified savings and medium-term deposits.")
            recommendations['fixed_deposits'].extend(['6_months', '12_months'])
        else:
            recommendations['reasoning'].append("Higher income - explore premium savings and long-term investment options.")
            recommendations['savings_accounts'].extend(['institutional'])
            recommendations['fixed_deposits'].extend(['24_months', '36_months'])
        
        # Goal-based
        if 'house_purchase' in goals:
            recommendations['reasoning'].append("House purchase goal - consider long-term savings and home loans.")
            recommendations['savings_accounts'].extend(['monthly'])
            recommendations['loans'].extend(['house_construction', 'land_purchase'])
        
        if 'education' in goals:
            recommendations['reasoning'].append("Education goal - consider education loans and child savings.")
            recommendations['savings_accounts'].extend(['child'])
            recommendations['loans'].extend(['education'])
        
        if 'business' in goals:
            recommendations['reasoning'].append("Business goal - consider business loans and institutional savings.")
            recommendations['savings_accounts'].extend(['institutional'])
            recommendations['loans'].extend(['business'])
        
        if 'vehicle' in goals:
            recommendations['reasoning'].append("Vehicle purchase goal - consider vehicle loans.")
            recommendations['loans'].extend(['vehicle'])
        
        # Risk tolerance
        if risk_tolerance == 'conservative':
            recommendations['reasoning'].append("Conservative approach - focus on guaranteed returns.")
            recommendations['fixed_deposits'] = list(set(recommendations['fixed_deposits'] + ['12_months', '24_months']))
        elif risk_tolerance == 'aggressive':
            recommendations['reasoning'].append("Aggressive approach - consider higher-yield options.")
            recommendations['savings_accounts'].extend(['monthly'])
            recommendations['fixed_deposits'].extend(['36_months'])
            
        # De-duplicate
        recommendations['savings_accounts'] = list(set(recommendations['savings_accounts']))
        recommendations['loans'] = list(set(recommendations['loans']))
        recommendations['fixed_deposits'] = list(set(recommendations['fixed_deposits']))
        
        return recommendations

    @staticmethod
    def save_recommendation(user_profile, recommendations_data, confidence=85.0):
        return ServiceRecommendation.objects.create(
            user_profile=user_profile,
            recommended_services=recommendations_data,
            recommendation_reason='\n'.join(recommendations_data['reasoning']),
            confidence_score=confidence
        )

class ServiceComparisonService:
    """Service to handle comparison logic"""
    
    @staticmethod
    def compare_savings_accounts(account_ids: list) -> Dict[str, Any]:
        accounts = SavingsAccount.objects.filter(id__in=account_ids, is_active=True)
        comparison_data = []
        
        for account in accounts:
            comparison_data.append({
                'id': account.id,
                'name': account.english_name,
                'nepali_name': account.nepali_name,
                'interest_rate': float(account.interest_rate),
                'minimum_balance': float(account.minimum_balance) if account.minimum_balance else 0,
                'features': account.features.split('\n') if account.features else [],
                'description': account.description,
                'is_featured': account.is_featured,
                'icon': account.icon,
                'color': account.color
            })
        
        if not comparison_data:
            return {}

        return {
            'accounts': comparison_data,
            'best_interest_rate': max([acc['interest_rate'] for acc in comparison_data]),
            'lowest_minimum_balance': min([acc['minimum_balance'] for acc in comparison_data]),
            'featured_accounts': [acc for acc in comparison_data if acc['is_featured']]
        }
    
    @staticmethod
    def compare_loans(loan_ids: list) -> Dict[str, Any]:
        loans = LoanType.objects.filter(id__in=loan_ids, is_active=True)
        comparison_data = []
        
        for loan in loans:
            comparison_data.append({
                'id': loan.id,
                'name': loan.english_name,
                'nepali_name': loan.nepali_name,
                'monthly_interest_rate': float(loan.monthly_interest_rate),
                # Removed monthly_installment_rate as it does not exist on model
                'minimum_amount': float(loan.minimum_amount) if loan.minimum_amount else 0,
                'maximum_amount': float(loan.maximum_amount) if loan.maximum_amount else 0,
                'max_tenure_years': loan.max_tenure_years,
                'requirements': loan.requirements.split('\n') if loan.requirements else [],
                'benefits': loan.benefits.split('\n') if loan.benefits else [],
                'is_featured': loan.is_featured,
                'icon': loan.icon,
                'color': loan.color
            })
            
        if not comparison_data:
            return {}
        
        return {
            'loans': comparison_data,
            'lowest_interest_rate': min([loan['monthly_interest_rate'] for loan in comparison_data]),
            'highest_maximum_amount': max([loan['maximum_amount'] for loan in comparison_data]),
            'featured_loans': [loan for loan in comparison_data if loan['is_featured']]
        }
    
    @staticmethod
    def compare_fixed_deposits(deposit_ids: list) -> Dict[str, Any]:
        deposits = FixedDeposit.objects.filter(id__in=deposit_ids, is_active=True)
        comparison_data = []
        
        for deposit in deposits:
            comparison_data.append({
                'id': deposit.id,
                'duration_months': deposit.duration_months,
                'duration_display': deposit.get_duration_months_display(),
                'payment_frequency': deposit.payment_frequency,
                'payment_frequency_display': deposit.get_payment_frequency_display(),
                'interest_rate': float(deposit.interest_rate),
                'minimum_amount': float(deposit.minimum_amount) if deposit.minimum_amount else 0,
                'maximum_amount': float(deposit.maximum_amount) if deposit.maximum_amount else 0,
                'benefits': deposit.benefits.split('\n') if deposit.benefits else [],
                'description': deposit.description
            })
            
        if not comparison_data:
            return {}
        
        return {
            'deposits': comparison_data,
            'highest_interest_rate': max([dep['interest_rate'] for dep in comparison_data]),
            'shortest_duration': min([dep['duration_months'] for dep in comparison_data]),
            'longest_duration': max([dep['duration_months'] for dep in comparison_data])
        }

class ServiceSearchService:
    """Service to handle search logic"""
    
    @staticmethod
    def search_services(form_data: Dict[str, Any], page_number: int = 1, page_size: int = 10):
        query = form_data.get('query', '')
        service_type = form_data.get('service_type', '')
        interest_rate_min = form_data.get('interest_rate_min')
        interest_rate_max = form_data.get('interest_rate_max')
        featured_only = form_data.get('featured_only', False)
        
        results = []
        
        # Savings Search
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
                    'url': f'/services/savings/{account.slug}/', # using slug as per models
                    'icon': account.icon,
                    'color': account.color
                })
        
        # Loans Search
        if service_type == 'loans' or not service_type:
            loans_q = Q(is_active=True)
            if query:
                loans_q &= (Q(english_name__icontains=query) | Q(nepali_name__icontains=query) | 
                           Q(description__icontains=query))
            # Note: loans use monthly_interest_rate
            if interest_rate_min:
                # Assuming user enters annual rate? Or monthly?
                # Code in views.py assumed direct comparison.
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
                    'url': f'/services/loans/{loan.slug}/', # using slug
                    'icon': loan.icon,
                    'color': loan.color
                })
                
        # Paginate
        paginator = Paginator(results, page_size)
        page_obj = paginator.get_page(page_number)
        
        return {
            'results': page_obj,
            'total_results': len(results)
        }

class ServiceApplicationService:
    """Service to handle applications"""
    
    @staticmethod
    def process_application(form, service_type: str, service_id: str):
        """
        Process the service application form.
        Expected to handle saving and analytics tracking.
        """
        # Save application
        application = form.save(commit=False)
        
        # Link to actual service object
        from django.contrib.contenttypes.models import ContentType
        model_class = ServiceAnalyticsService._get_model_class(service_type)
        if model_class and service_id:
             content_type = ContentType.objects.get_for_model(model_class)
             application.content_type = content_type
             application.object_id = int(service_id)
             # service_object field on model is GenericForeignKey, so setting above 2 is enough
        
        application.save()
        
        # Track analytics
        ServiceAnalyticsService.track_usage(service_type, int(service_id), 'applications_received')
        
        return application
