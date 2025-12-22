import math
from decimal import Decimal
from typing import Dict, Any
from django.utils.translation import gettext_lazy as _


class FinancialCalculator:
    """
    Utility class for financial calculations.
    
    Provides static methods for calculating loan EMIs, savings maturity amounts,
    and fixed deposit returns. All calculations use Decimal for precision
    and return detailed breakdowns of principal, interest, and totals.
    
    Usage:
        calculator = FinancialCalculator()
        emi_result = calculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=60
        )
    """
    
    @staticmethod
    def calculate_loan_emi(principal: Decimal, annual_rate: Decimal, tenure_months: int, 
                          payment_frequency: str = 'monthly') -> Dict[str, Any]:
        """
        Calculate Equated Monthly Installment (EMI) for loans.
        
        Uses the standard EMI formula to calculate monthly or quarterly payments
        based on principal amount, annual interest rate, and loan tenure.
        Handles zero-interest loans (interest-free) as a special case.
        
        Args:
            principal: Loan principal amount (must be positive)
            annual_rate: Annual interest rate as percentage (e.g., 12 for 12%)
            tenure_months: Loan tenure in months (must be positive)
            payment_frequency: Payment frequency - 'monthly' (default) or 'quarterly'
            
        Returns:
            Dictionary containing:
                - emi: Equated monthly/quarterly installment amount
                - total_amount: Total amount to be paid (principal + interest)
                - total_interest: Total interest amount
                - principal: Original principal amount
                - tenure_periods: Number of payment periods
                - rate_per_period: Interest rate per payment period (as percentage)
                - payment_frequency: Payment frequency used
                
        Example:
            >>> from decimal import Decimal
            >>> result = FinancialCalculator.calculate_loan_emi(
            ...     principal=Decimal('100000'),
            ...     annual_rate=Decimal('12'),
            ...     tenure_months=60
            ... )
            >>> result['emi']
            Decimal('2224.44')
            >>> result['total_interest']
            Decimal('33466.40')
            
        Note:
            For quarterly payments, tenure is converted to quarters (months / 3).
            Interest rate is converted to per-period rate automatically.
        """
        if payment_frequency == 'quarterly':
            # Convert to quarterly payments
            tenure_periods = tenure_months // 3
            rate_per_period = annual_rate / 400  # Quarterly rate
        else:
            tenure_periods = tenure_months
            rate_per_period = annual_rate / 1200  # Monthly rate
        
        if rate_per_period == 0:
            emi = principal / tenure_periods
        else:
            emi = principal * rate_per_period * ((1 + rate_per_period) ** tenure_periods) / \
                  (((1 + rate_per_period) ** tenure_periods) - 1)
        
        total_amount = emi * tenure_periods
        total_interest = total_amount - principal
        
        return {
            'emi': round(emi, 2),
            'total_amount': round(total_amount, 2),
            'total_interest': round(total_interest, 2),
            'principal': principal,
            'tenure_periods': tenure_periods,
            'rate_per_period': rate_per_period * 100,
            'payment_frequency': payment_frequency
        }
    
    @staticmethod
    def calculate_savings_maturity(monthly_deposit: Decimal, annual_rate: Decimal, 
                                 tenure_years: int) -> Dict[str, Any]:
        """
        Calculate savings account maturity amount with monthly deposits.
        
        Calculates the future value of a savings account where regular monthly
        deposits are made and interest is compounded monthly. Uses the future
        value of annuity formula.
        
        Args:
            monthly_deposit: Monthly deposit amount (must be positive)
            annual_rate: Annual interest rate as percentage (e.g., 6 for 6%)
            tenure_years: Savings tenure in years (must be positive)
            
        Returns:
            Dictionary containing:
                - maturity_amount: Total amount at maturity (deposits + interest)
                - total_deposits: Total amount deposited over tenure
                - interest_earned: Total interest earned
                - monthly_deposit: Monthly deposit amount
                - tenure_years: Savings tenure in years
                - annual_rate: Annual interest rate used
                
        Example:
            >>> from decimal import Decimal
            >>> result = FinancialCalculator.calculate_savings_maturity(
            ...     monthly_deposit=Decimal('5000'),
            ...     annual_rate=Decimal('6'),
            ...     tenure_years=5
            ... )
            >>> result['maturity_amount']
            Decimal('348850.00')
            >>> result['interest_earned']
            Decimal('48850.00')
            
        Formula:
            FV = PMT × [((1 + r)^n - 1) / r]
            Where:
                FV = Future Value
                PMT = Monthly Payment
                r = Monthly Interest Rate
                n = Number of Months
        """
        monthly_rate = annual_rate / 1200
        total_months = tenure_years * 12
        total_deposits = monthly_deposit * total_months
        
        if monthly_rate == 0:
            maturity_amount = total_deposits
        else:
            maturity_amount = monthly_deposit * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
        
        interest_earned = maturity_amount - total_deposits
        
        return {
            'maturity_amount': round(maturity_amount, 2),
            'total_deposits': round(total_deposits, 2),
            'interest_earned': round(interest_earned, 2),
            'monthly_deposit': monthly_deposit,
            'tenure_years': tenure_years,
            'annual_rate': annual_rate
        }
    
    @staticmethod
    def calculate_fixed_deposit_maturity(principal: Decimal, annual_rate: Decimal, 
                                       tenure_months: int, payment_frequency: str) -> Dict[str, Any]:
        """
        Calculate fixed deposit maturity amount based on payment frequency.
        
        Calculates the maturity amount for fixed deposits with different interest
        payment frequencies. Supports monthly, quarterly, and lump sum (compounded)
        payment options.
        
        Args:
            principal: Fixed deposit principal amount (must be positive)
            annual_rate: Annual interest rate as percentage (e.g., 8 for 8%)
            tenure_months: Deposit tenure in months (must be positive)
            payment_frequency: Interest payment frequency:
                - 'monthly': Interest paid monthly (simple interest)
                - 'quarterly': Interest paid quarterly (simple interest)
                - 'lump_sum': Interest compounded and paid at maturity
                
        Returns:
            Dictionary containing:
                - maturity_amount: Total amount at maturity (principal + interest)
                - principal: Original deposit amount
                - interest_earned: Total interest earned
                - tenure_months: Deposit tenure in months
                - annual_rate: Annual interest rate used
                - payment_frequency: Payment frequency used
                
        Example:
            >>> from decimal import Decimal
            >>> # Lump sum (compounded)
            >>> result = FinancialCalculator.calculate_fixed_deposit_maturity(
            ...     principal=Decimal('100000'),
            ...     annual_rate=Decimal('8'),
            ...     tenure_months=12,
            ...     payment_frequency='lump_sum'
            ... )
            >>> result['maturity_amount']
            Decimal('108300.00')
            
            >>> # Monthly interest payments
            >>> result = FinancialCalculator.calculate_fixed_deposit_maturity(
            ...     principal=Decimal('100000'),
            ...     annual_rate=Decimal('8'),
            ...     tenure_months=12,
            ...     payment_frequency='monthly'
            ... )
            >>> result['interest_earned']
            Decimal('8000.00')
            
        Note:
            - Monthly/Quarterly: Simple interest calculation (interest not compounded)
            - Lump Sum: Compound interest calculation (interest compounded monthly)
            - For quarterly payments, tenure is converted to quarters (months / 3)
        """
        monthly_rate = annual_rate / 1200
        
        if payment_frequency == 'lump_sum':
            # Compound interest calculation
            maturity_amount = principal * ((1 + monthly_rate) ** tenure_months)
        elif payment_frequency == 'quarterly':
            # Quarterly interest payments
            quarterly_rate = annual_rate / 400
            quarters = tenure_months // 3
            quarterly_interest = principal * quarterly_rate
            total_interest = quarterly_interest * quarters
            maturity_amount = principal + total_interest
        else:  # monthly
            # Monthly interest payments
            monthly_interest = principal * monthly_rate
            total_interest = monthly_interest * tenure_months
            maturity_amount = principal + total_interest
        
        interest_earned = maturity_amount - principal
        
        return {
            'maturity_amount': round(maturity_amount, 2),
            'principal': principal,
            'interest_earned': round(interest_earned, 2),
            'tenure_months': tenure_months,
            'annual_rate': annual_rate,
            'payment_frequency': payment_frequency
        }



