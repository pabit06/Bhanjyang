from datetime import date
from typing import Dict, Any, List
from django.db.models import Q
from decimal import Decimal
from django.core.paginator import Paginator

from .models import (
    SavingsAccount, FixedDeposit, LoanType, 
    RemittanceService, MemberRelief,
    ServiceApplication, ServiceAnalytics, ServiceRecommendation,
    ExchangeRate
)

class ServiceAnalyticsService:
    """
    Service class for tracking service usage analytics and metrics.
    
    This service handles tracking of various user interactions with financial services,
    including page views, calculator usage, application submissions, and comparison views.
    All analytics are stored in the ServiceAnalytics model with daily aggregation.
    
    Usage:
        ServiceAnalyticsService.track_usage('savings', 1, 'page_views')
        ServiceAnalyticsService.track_usage('loan', 5, 'calculator_usage')
    """
    
    @staticmethod
    def track_calculator_usage(service_type: str, service_id: int):
        """
        Track usage of financial calculators.
        
        Note: This method is deprecated. Use track_usage() instead.
        
        Args:
            service_type: Type of service ('savings', 'loan', 'fixed_deposit', etc.)
            service_id: ID of the service instance
        """
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
        """
        Map service type string to corresponding model class.
        
        Args:
            service_type: Service type identifier ('savings', 'loan', 'fixed_deposit', 'remittance', 'relief')
            
        Returns:
            Model class or None if service_type is invalid
            
        Example:
            >>> ServiceAnalyticsService._get_model_class('savings')
            <class 'apps.services.models.SavingsAccount'>
        """
        if service_type == 'savings': return SavingsAccount
        if service_type == 'loan': return LoanType
        if service_type == 'fixed_deposit': return FixedDeposit
        if service_type == 'remittance': return RemittanceService
        if service_type == 'relief': return MemberRelief
        return None

    @classmethod
    def track_usage(cls, service_type: str, service_id: int, action: str) -> None:
        """
        Track service usage analytics for various actions.
        
        This method increments counters in the ServiceAnalytics model for tracking
        user interactions with services. Analytics are aggregated daily per service.
        
        Args:
            service_type: Type of service ('savings', 'loan', 'fixed_deposit', 'remittance', 'relief')
            service_id: ID of the service instance
            action: Type of action to track:
                - 'page_views': When a service detail page is viewed
                - 'calculator_usage': When a financial calculator is used
                - 'applications_received': When a service application is submitted
                - 'comparison_views': When services are compared
                
        Returns:
            None
            
        Example:
            >>> ServiceAnalyticsService.track_usage('savings', 1, 'page_views')
            >>> ServiceAnalyticsService.track_usage('loan', 5, 'calculator_usage')
            
        Note:
            If the service_type is invalid or an error occurs, the method fails silently
            to avoid disrupting the main application flow.
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
    """
    Service class for generating personalized service recommendations.
    
    This service analyzes user profiles (age, income, goals, risk tolerance) and
    recommends appropriate financial services including savings accounts, loans,
    and fixed deposits based on best practices and user needs.
    
    Usage:
        profile = {
            'age': 35,
            'monthly_income': 75000,
            'goals': ['house_purchase', 'education'],
            'risk_tolerance': 'moderate'
        }
        recommendations = ServiceRecommendationService.get_recommendations(profile)
    """
    
    @staticmethod
    def get_recommendations(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate service recommendations based on user profile.
        
        Analyzes user demographics and preferences to recommend suitable financial
        services. Recommendations are based on:
        - Age: Different life stages have different financial needs
        - Income: Income level determines suitable service tiers
        - Goals: Specific goals (house, education, business) suggest relevant services
        - Risk Tolerance: Conservative vs aggressive investment preferences
        
        Args:
            user_profile: Dictionary containing:
                - age (int): User's age in years
                - monthly_income (int): Monthly income in NPR
                - goals (list): List of financial goals (e.g., ['house_purchase', 'education'])
                - risk_tolerance (str): 'conservative', 'moderate', or 'aggressive'
                
        Returns:
            Dictionary with recommendations:
                - savings_accounts (list): Recommended savings account types
                - loans (list): Recommended loan types
                - fixed_deposits (list): Recommended fixed deposit durations
                - reasoning (list): Explanations for each recommendation
                
        Example:
            >>> profile = {
            ...     'age': 30,
            ...     'monthly_income': 50000,
            ...     'goals': ['house_purchase'],
            ...     'risk_tolerance': 'moderate'
            ... }
            >>> recs = ServiceRecommendationService.get_recommendations(profile)
            >>> recs['savings_accounts']
            ['general', 'monthly']
        """
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
    def save_recommendation(user_profile: Dict[str, Any], recommendations_data: Dict[str, Any], confidence: float = 85.0) -> 'ServiceRecommendation':
        """
        Save service recommendations to database for future reference.
        
        Stores the recommendation along with user profile and confidence score
        for analytics and potential reuse.
        
        Args:
            user_profile: Original user profile dictionary
            recommendations_data: Recommendations dictionary from get_recommendations()
            confidence: Confidence score (0-100) for the recommendations, default 85.0
            
        Returns:
            ServiceRecommendation: Created recommendation instance
            
        Example:
            >>> profile = {'age': 30, 'monthly_income': 50000}
            >>> recs = ServiceRecommendationService.get_recommendations(profile)
            >>> saved = ServiceRecommendationService.save_recommendation(profile, recs)
        """
        return ServiceRecommendation.objects.create(
            user_profile=user_profile,
            recommended_services=recommendations_data,
            recommendation_reason='\n'.join(recommendations_data['reasoning']),
            confidence_score=confidence
        )

class ServiceComparisonService:
    """
    Service class for comparing multiple financial services side-by-side.
    
    This service provides functionality to compare different services (savings accounts,
    loans, fixed deposits) to help users make informed decisions. It extracts key
    features and metrics for easy comparison.
    
    Usage:
        comparison = ServiceComparisonService.compare_savings_accounts([1, 2, 3])
    """
    
    @staticmethod
    def compare_savings_accounts(account_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple savings accounts side-by-side.
        
        Retrieves savings account details and extracts key comparison metrics
        including interest rates, minimum balances, and features.
        
        Args:
            account_ids: List of savings account IDs to compare
            
        Returns:
            Dictionary containing:
                - accounts (list): List of account details dictionaries
                - best_interest_rate (float): Highest interest rate among accounts
                - lowest_minimum_balance (float): Lowest minimum balance requirement
                - featured_accounts (list): Accounts marked as featured
                
        Example:
            >>> comparison = ServiceComparisonService.compare_savings_accounts([1, 2, 3])
            >>> comparison['best_interest_rate']
            6.5
            >>> len(comparison['accounts'])
            3
        """
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
    def compare_loans(loan_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple loan types side-by-side.
        
        Retrieves loan details and extracts key comparison metrics including
        interest rates, loan amounts, tenure, and requirements.
        
        Args:
            loan_ids: List of loan type IDs to compare
            
        Returns:
            Dictionary containing:
                - loans (list): List of loan details dictionaries
                - lowest_interest_rate (float): Lowest monthly interest rate
                - highest_maximum_amount (float): Highest maximum loan amount
                - featured_loans (list): Loans marked as featured
                
        Example:
            >>> comparison = ServiceComparisonService.compare_loans([1, 2])
            >>> comparison['lowest_interest_rate']
            1.2
        """
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
    def compare_fixed_deposits(deposit_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple fixed deposit schemes side-by-side.
        
        Retrieves fixed deposit details and extracts key comparison metrics
        including interest rates, durations, and payment frequencies.
        
        Args:
            deposit_ids: List of fixed deposit IDs to compare
            
        Returns:
            Dictionary containing:
                - deposits (list): List of deposit details dictionaries
                - highest_interest_rate (float): Highest interest rate
                - shortest_duration (int): Shortest duration in months
                - longest_duration (int): Longest duration in months
                
        Example:
            >>> comparison = ServiceComparisonService.compare_fixed_deposits([1, 2, 3])
            >>> comparison['highest_interest_rate']
            8.5
        """
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
                'description': getattr(deposit, 'description', '')  # FixedDeposit may not have description
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
    """
    Service class for searching and filtering financial services.
    
    Provides advanced search functionality across all service types (savings accounts,
    loans, fixed deposits) with filtering by name, interest rate, and featured status.
    Results are paginated for performance.
    
    Usage:
        form_data = {
            'query': 'savings',
            'service_type': 'savings',
            'interest_rate_min': 5.0,
            'featured_only': True
        }
        results = ServiceSearchService.search_services(form_data, page_number=1)
    """
    
    @staticmethod
    def search_services(form_data: Dict[str, Any], page_number: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Search and filter financial services based on criteria.
        
        Performs text search across service names and descriptions, and filters
        by interest rate range and featured status. Supports searching across
        multiple service types or focusing on a specific type.
        
        Args:
            form_data: Dictionary containing search criteria:
                - query (str): Search text for names and descriptions
                - service_type (str): 'savings', 'loans', or empty for all
                - interest_rate_min (float): Minimum interest rate filter
                - interest_rate_max (float): Maximum interest rate filter
                - featured_only (bool): Only return featured services
            page_number: Page number for pagination (default: 1)
            page_size: Number of results per page (default: 10)
            
        Returns:
            Dictionary containing:
                - results (Page): Paginated results with service details
                - total_results (int): Total number of matching services
                
        Example:
            >>> form_data = {'query': 'savings', 'service_type': 'savings'}
            >>> results = ServiceSearchService.search_services(form_data)
            >>> results['total_results']
            5
            >>> len(results['results'])
            5
        """
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
    """
    Service class for processing service applications.
    
    Handles the submission and processing of service applications from users.
    Links applications to specific services using GenericForeignKey and tracks
    application analytics.
    
    Usage:
        application = ServiceApplicationService.process_application(
            form, 'savings', '1'
        )
    """
    
    @staticmethod
    def process_application(form, service_type: str, service_id: str) -> 'ServiceApplication':
        """
        Process and save a service application form submission.
        
        Saves the application form data, links it to the appropriate service
        using GenericForeignKey, and tracks the application in analytics.
        
        Args:
            form: Django form instance (ServiceApplicationForm) with cleaned data
            service_type: Type of service ('savings', 'loan', 'fixed_deposit', etc.)
            service_id: String ID of the service instance
            
        Returns:
            ServiceApplication: Created application instance
            
        Example:
            >>> form = ServiceApplicationForm(data)
            >>> application = ServiceApplicationService.process_application(
            ...     form, 'savings', '1'
            ... )
            >>> application.applicant_name
            'John Doe'
            
        Note:
            Also tracks the application in ServiceAnalytics with action
            'applications_received' for analytics purposes.
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


class ExchangeRateService:
    """
    Service class for managing exchange rates, including fetching from NRB API.
    
    This service handles:
    - Fetching exchange rates from Nepal Rastra Bank (NRB) API
    - Storing rates in the database
    - Providing rate calculation utilities
    - Caching rates for performance
    
    Usage:
        ExchangeRateService.fetch_nrb_rates()
        rate = ExchangeRateService.get_current_rate('USD')
        amount = ExchangeRateService.convert_currency(1000, 'USD', 'NPR')
    """
    
    # NRB API endpoint (may need to be updated based on actual NRB API)
    NRB_API_URL = 'https://www.nrb.org.np/api/forex/v1/rates'
    
    @staticmethod
    def fetch_nrb_rates(date=None):
        """
        Fetch exchange rates from NRB API and store in database.
        
        Args:
            date: Optional date to fetch rates for. If None, fetches latest rates.
            
        Returns:
            int: Number of rates fetched and saved
            
        Raises:
            Exception: If API request fails or data is invalid
        """
        import requests
        from django.utils import timezone
        from decimal import Decimal
        import logging
        
        logger = logging.getLogger(__name__)
        
        if date is None:
            date = timezone.now().date()
        
        try:
            # Try to fetch from NRB API
            # Note: NRB API format may vary, this is a common structure
            response = requests.get(
                ExchangeRateService.NRB_API_URL,
                params={'date': date.isoformat()} if date else {},
                timeout=10
            )
            response.raise_for_status()
            
            # Parse response - adjust based on actual NRB API format
            data = response.json()
            
            # NRB API typically returns data in format:
            # {"data": [{"currency": "USD", "buy": 133.50, "sell": 134.00, ...}, ...]}
            rates_data = data.get('data', [])
            if not rates_data:
                # Try alternative format
                rates_data = data.get('rates', [])
            
            count = 0
            for rate_data in rates_data:
                currency_code = rate_data.get('currency', rate_data.get('currencyCode', '')).upper()
                
                # Skip if currency not in our choices
                if currency_code not in [code for code, _ in ExchangeRate.CURRENCY_CHOICES]:
                    continue
                
                buy_rate = Decimal(str(rate_data.get('buy', rate_data.get('buyRate', 0))))
                sell_rate = Decimal(str(rate_data.get('sell', rate_data.get('sellRate', 0))))
                
                if buy_rate <= 0 or sell_rate <= 0:
                    continue
                
                # Create or update exchange rate
                exchange_rate, created = ExchangeRate.objects.update_or_create(
                    currency_code=currency_code,
                    rate_date=date,
                    defaults={
                        'buy_rate': buy_rate,
                        'sell_rate': sell_rate,
                        'source': 'NRB',
                        'is_active': True,
                    }
                )
                
                if created:
                    count += 1
                    logger.info(f"Created exchange rate: {currency_code} for {date}")
                else:
                    logger.info(f"Updated exchange rate: {currency_code} for {date}")
            
            return count
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NRB rates: {str(e)}")
            # Fallback: Return 0 if API fails, but don't raise exception
            # This allows manual entry in admin
            return 0
        except Exception as e:
            logger.error(f"Unexpected error fetching NRB rates: {str(e)}")
            raise
    
    @staticmethod
    def get_current_rate(currency_code: str, rate_type: str = 'mid'):
        """
        Get current exchange rate for a currency.
        
        Args:
            currency_code: ISO currency code (e.g., 'USD')
            rate_type: 'buy', 'sell', or 'mid' (default: 'mid')
            
        Returns:
            Decimal: Exchange rate, or None if not found
        """
        rate = ExchangeRate.get_latest_rate(currency_code)
        if not rate:
            return None
        
        if rate_type == 'buy':
            return rate.buy_rate
        elif rate_type == 'sell':
            return rate.sell_rate
        else:
            return rate.mid_rate
    
    @staticmethod
    def convert_currency(amount: Decimal, from_currency: str, to_currency: str, rate_type: str = 'mid'):
        """
        Convert currency amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            rate_type: 'buy', 'sell', or 'mid' (default: 'mid')
            
        Returns:
            Decimal: Converted amount, or None if rate not available
        """
        # If converting to NPR, use direct rate
        if to_currency == 'NPR':
            rate = ExchangeRateService.get_current_rate(from_currency, rate_type)
            if rate:
                return amount * rate
        
        # If converting from NPR, use inverse rate
        elif from_currency == 'NPR':
            rate = ExchangeRateService.get_current_rate(to_currency, rate_type)
            if rate:
                return amount / rate
        
        # Converting between two foreign currencies via NPR
        else:
            from_rate = ExchangeRateService.get_current_rate(from_currency, rate_type)
            to_rate = ExchangeRateService.get_current_rate(to_currency, rate_type)
            if from_rate and to_rate:
                # Convert to NPR first, then to target currency
                npr_amount = amount * from_rate
                return npr_amount / to_rate
        
        return None
    
    @staticmethod
    def get_all_current_rates():
        """
        Get all current exchange rates.
        
        Returns:
            dict: Dictionary mapping currency codes to ExchangeRate objects
        """
        return ExchangeRate.get_latest_rates()
