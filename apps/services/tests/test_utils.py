"""
Comprehensive tests for FinancialCalculator utility class
"""
from decimal import Decimal
from django.test import TestCase

from apps.services.utils import FinancialCalculator


class FinancialCalculatorTest(TestCase):
    """Test suite for FinancialCalculator"""
    
    def test_calculate_loan_emi_monthly_basic(self):
        """Test basic monthly EMI calculation"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=12
        )
        
        self.assertIn('emi', result)
        self.assertIn('total_amount', result)
        self.assertIn('total_interest', result)
        self.assertIn('principal', result)
        self.assertIn('tenure_periods', result)
        self.assertIn('rate_per_period', result)
        self.assertIn('payment_frequency', result)
        
        self.assertEqual(result['principal'], Decimal('100000'))
        self.assertEqual(result['tenure_periods'], 12)
        self.assertEqual(result['payment_frequency'], 'monthly')
        self.assertGreater(result['emi'], 0)
        self.assertGreater(result['total_amount'], result['principal'])
        self.assertGreater(result['total_interest'], 0)
    
    def test_calculate_loan_emi_quarterly(self):
        """Test quarterly EMI calculation"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=12,
            payment_frequency='quarterly'
        )
        
        self.assertEqual(result['payment_frequency'], 'quarterly')
        self.assertEqual(result['tenure_periods'], 4)  # 12 months / 3
        self.assertGreater(result['emi'], 0)
    
    def test_calculate_loan_emi_zero_interest(self):
        """Test EMI calculation with zero interest"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('0'),
            tenure_months=12
        )
        
        # With zero interest, EMI should be principal / tenure
        expected_emi = Decimal('100000') / 12
        self.assertEqual(result['emi'], round(expected_emi, 2))
        self.assertEqual(result['total_interest'], Decimal('0'))
        self.assertEqual(result['total_amount'], result['principal'])
    
    def test_calculate_loan_emi_high_interest(self):
        """Test EMI calculation with high interest rate"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('24'),
            tenure_months=12
        )
        
        self.assertGreater(result['emi'], 0)
        self.assertGreater(result['total_interest'], 0)
        # High interest should result in higher EMI (amortized, not simple interest)
        # With 24% annual rate, total should be around 113,471 (not 124,000 for simple interest)
        self.assertGreater(result['total_amount'], Decimal('110000'))
        self.assertLess(result['total_amount'], Decimal('120000'))  # Amortized interest is less than simple
    
    def test_calculate_loan_emi_long_tenure(self):
        """Test EMI calculation with long tenure"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=360  # 30 years
        )
        
        self.assertEqual(result['tenure_periods'], 360)
        self.assertGreater(result['emi'], 0)
        # Longer tenure should result in lower EMI but higher total interest
        self.assertGreater(result['total_interest'], Decimal('100000'))
    
    def test_calculate_loan_emi_short_tenure(self):
        """Test EMI calculation with short tenure"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=1
        )
        
        self.assertEqual(result['tenure_periods'], 1)
        self.assertGreater(result['emi'], 0)
        # Short tenure should result in higher EMI but lower total interest
    
    def test_calculate_loan_emi_large_principal(self):
        """Test EMI calculation with large principal"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('10000000'),
            annual_rate=Decimal('12'),
            tenure_months=60
        )
        
        self.assertEqual(result['principal'], Decimal('10000000'))
        self.assertGreater(result['emi'], Decimal('200000'))  # Should be substantial
    
    def test_calculate_loan_emi_small_principal(self):
        """Test EMI calculation with small principal"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('1000'),
            annual_rate=Decimal('12'),
            tenure_months=12
        )
        
        self.assertEqual(result['principal'], Decimal('1000'))
        self.assertGreater(result['emi'], 0)
        self.assertLess(result['emi'], Decimal('100'))  # Should be reasonable
    
    def test_calculate_loan_emi_quarterly_conversion(self):
        """Test that quarterly payments convert tenure correctly"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=15,  # 5 quarters
            payment_frequency='quarterly'
        )
        
        self.assertEqual(result['tenure_periods'], 5)  # 15 / 3 = 5
    
    def test_calculate_savings_maturity_basic(self):
        """Test basic savings maturity calculation"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('6'),
            tenure_years=5
        )
        
        self.assertIn('maturity_amount', result)
        self.assertIn('total_deposits', result)
        self.assertIn('interest_earned', result)
        self.assertIn('monthly_deposit', result)
        self.assertIn('tenure_years', result)
        self.assertIn('annual_rate', result)
        
        self.assertEqual(result['monthly_deposit'], Decimal('5000'))
        self.assertEqual(result['tenure_years'], 5)
        self.assertEqual(result['annual_rate'], Decimal('6'))
        
        # Total deposits should be 5000 * 12 * 5 = 300000
        self.assertEqual(result['total_deposits'], Decimal('300000'))
        self.assertGreater(result['maturity_amount'], result['total_deposits'])
        self.assertGreater(result['interest_earned'], 0)
    
    def test_calculate_savings_maturity_zero_interest(self):
        """Test savings maturity with zero interest"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('0'),
            tenure_years=5
        )
        
        # With zero interest, maturity should equal total deposits
        self.assertEqual(result['maturity_amount'], result['total_deposits'])
        self.assertEqual(result['interest_earned'], Decimal('0'))
    
    def test_calculate_savings_maturity_high_interest(self):
        """Test savings maturity with high interest rate"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('12'),
            tenure_years=5
        )
        
        self.assertGreater(result['maturity_amount'], result['total_deposits'])
        # Higher interest should result in more interest earned
        self.assertGreater(result['interest_earned'], Decimal('50000'))
    
    def test_calculate_savings_maturity_long_tenure(self):
        """Test savings maturity with long tenure"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('6'),
            tenure_years=20
        )
        
        self.assertEqual(result['tenure_years'], 20)
        # Total deposits should be 5000 * 12 * 20 = 1200000
        self.assertEqual(result['total_deposits'], Decimal('1200000'))
        self.assertGreater(result['maturity_amount'], result['total_deposits'])
    
    def test_calculate_savings_maturity_short_tenure(self):
        """Test savings maturity with short tenure"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('6'),
            tenure_years=1
        )
        
        self.assertEqual(result['tenure_years'], 1)
        # Total deposits should be 5000 * 12 = 60000
        self.assertEqual(result['total_deposits'], Decimal('60000'))
        self.assertGreater(result['maturity_amount'], result['total_deposits'])
    
    def test_calculate_savings_maturity_large_deposit(self):
        """Test savings maturity with large monthly deposit"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('50000'),
            annual_rate=Decimal('6'),
            tenure_years=5
        )
        
        self.assertEqual(result['monthly_deposit'], Decimal('50000'))
        # Total deposits should be 50000 * 12 * 5 = 3000000
        self.assertEqual(result['total_deposits'], Decimal('3000000'))
        self.assertGreater(result['maturity_amount'], result['total_deposits'])
    
    def test_calculate_savings_maturity_small_deposit(self):
        """Test savings maturity with small monthly deposit"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('100'),
            annual_rate=Decimal('6'),
            tenure_years=5
        )
        
        self.assertEqual(result['monthly_deposit'], Decimal('100'))
        # Total deposits should be 100 * 12 * 5 = 6000
        self.assertEqual(result['total_deposits'], Decimal('6000'))
        self.assertGreater(result['maturity_amount'], result['total_deposits'])
    
    def test_calculate_fixed_deposit_maturity_lump_sum(self):
        """Test fixed deposit maturity with lump sum payment"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=12,
            payment_frequency='lump_sum'
        )
        
        self.assertIn('maturity_amount', result)
        self.assertIn('principal', result)
        self.assertIn('interest_earned', result)
        self.assertIn('tenure_months', result)
        self.assertIn('annual_rate', result)
        self.assertIn('payment_frequency', result)
        
        self.assertEqual(result['principal'], Decimal('100000'))
        self.assertEqual(result['tenure_months'], 12)
        self.assertEqual(result['annual_rate'], Decimal('8'))
        self.assertEqual(result['payment_frequency'], 'lump_sum')
        
        # Lump sum uses compound interest, so should be higher than simple interest
        self.assertGreater(result['maturity_amount'], Decimal('108000'))
        self.assertGreater(result['interest_earned'], Decimal('8000'))
    
    def test_calculate_fixed_deposit_maturity_monthly(self):
        """Test fixed deposit maturity with monthly interest payments"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=12,
            payment_frequency='monthly'
        )
        
        self.assertEqual(result['payment_frequency'], 'monthly')
        # Monthly uses simple interest: 100000 * 0.08 = 8000
        expected_interest = Decimal('100000') * Decimal('0.08')
        self.assertEqual(result['interest_earned'], round(expected_interest, 2))
        self.assertEqual(result['maturity_amount'], Decimal('108000'))
    
    def test_calculate_fixed_deposit_maturity_quarterly(self):
        """Test fixed deposit maturity with quarterly interest payments"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=12,
            payment_frequency='quarterly'
        )
        
        self.assertEqual(result['payment_frequency'], 'quarterly')
        # Quarterly: 12 months = 4 quarters, quarterly rate = 8% / 4 = 2%
        # Interest per quarter = 100000 * 0.02 = 2000
        # Total interest = 2000 * 4 = 8000
        expected_interest = Decimal('8000')
        self.assertEqual(result['interest_earned'], expected_interest)
        self.assertEqual(result['maturity_amount'], Decimal('108000'))
    
    def test_calculate_fixed_deposit_maturity_long_tenure(self):
        """Test fixed deposit maturity with long tenure"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=36,
            payment_frequency='lump_sum'
        )
        
        self.assertEqual(result['tenure_months'], 36)
        # Longer tenure should result in more interest (compound)
        self.assertGreater(result['maturity_amount'], Decimal('125000'))
        self.assertGreater(result['interest_earned'], Decimal('25000'))
    
    def test_calculate_fixed_deposit_maturity_short_tenure(self):
        """Test fixed deposit maturity with short tenure"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=3,
            payment_frequency='lump_sum'
        )
        
        self.assertEqual(result['tenure_months'], 3)
        # Short tenure should result in less interest
        self.assertLess(result['maturity_amount'], Decimal('103000'))
        self.assertLess(result['interest_earned'], Decimal('3000'))
    
    def test_calculate_fixed_deposit_maturity_high_rate(self):
        """Test fixed deposit maturity with high interest rate"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=12,
            payment_frequency='lump_sum'
        )
        
        self.assertEqual(result['annual_rate'], Decimal('12'))
        # Higher rate should result in more interest
        self.assertGreater(result['maturity_amount'], Decimal('112000'))
        self.assertGreater(result['interest_earned'], Decimal('12000'))
    
    def test_calculate_fixed_deposit_maturity_zero_interest(self):
        """Test fixed deposit maturity with zero interest"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('0'),
            tenure_months=12,
            payment_frequency='lump_sum'
        )
        
        # With zero interest, maturity should equal principal
        self.assertEqual(result['maturity_amount'], Decimal('100000'))
        self.assertEqual(result['interest_earned'], Decimal('0'))
    
    def test_calculate_fixed_deposit_maturity_large_principal(self):
        """Test fixed deposit maturity with large principal"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('10000000'),
            annual_rate=Decimal('8'),
            tenure_months=12,
            payment_frequency='lump_sum'
        )
        
        self.assertEqual(result['principal'], Decimal('10000000'))
        self.assertGreater(result['maturity_amount'], Decimal('10800000'))
        self.assertGreater(result['interest_earned'], Decimal('800000'))
    
    def test_calculate_fixed_deposit_maturity_quarterly_odd_months(self):
        """Test quarterly payment with tenure not divisible by 3"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=14,  # 14 months = 4 quarters (14 // 3 = 4)
            payment_frequency='quarterly'
        )
        
        # Should use integer division: 14 // 3 = 4 quarters
        # Interest = 100000 * 0.02 * 4 = 8000
        self.assertEqual(result['interest_earned'], Decimal('8000'))
    
    def test_calculate_fixed_deposit_maturity_comparison(self):
        """Test that lump_sum gives higher returns than monthly/quarterly"""
        principal = Decimal('100000')
        rate = Decimal('8')
        tenure = 12
        
        lump_sum = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal, rate, tenure, 'lump_sum'
        )
        monthly = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal, rate, tenure, 'monthly'
        )
        quarterly = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal, rate, tenure, 'quarterly'
        )
        
        # Lump sum (compound) should give highest return
        self.assertGreater(lump_sum['maturity_amount'], monthly['maturity_amount'])
        self.assertGreater(lump_sum['maturity_amount'], quarterly['maturity_amount'])
        # Monthly and quarterly should be equal (both simple interest)
        self.assertEqual(monthly['maturity_amount'], quarterly['maturity_amount'])
    
    def test_calculate_loan_emi_result_structure(self):
        """Test that loan EMI result has correct structure and types"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12'),
            tenure_months=12
        )
        
        # Check all required keys exist
        required_keys = ['emi', 'total_amount', 'total_interest', 'principal', 
                        'tenure_periods', 'rate_per_period', 'payment_frequency']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check types
        self.assertIsInstance(result['emi'], Decimal)
        self.assertIsInstance(result['total_amount'], Decimal)
        self.assertIsInstance(result['total_interest'], Decimal)
        self.assertIsInstance(result['principal'], Decimal)
        self.assertIsInstance(result['tenure_periods'], int)
        self.assertIsInstance(result['rate_per_period'], Decimal)
        self.assertIsInstance(result['payment_frequency'], str)
    
    def test_calculate_savings_maturity_result_structure(self):
        """Test that savings maturity result has correct structure and types"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('6'),
            tenure_years=5
        )
        
        # Check all required keys exist
        required_keys = ['maturity_amount', 'total_deposits', 'interest_earned',
                        'monthly_deposit', 'tenure_years', 'annual_rate']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check types
        self.assertIsInstance(result['maturity_amount'], Decimal)
        self.assertIsInstance(result['total_deposits'], Decimal)
        self.assertIsInstance(result['interest_earned'], Decimal)
        self.assertIsInstance(result['monthly_deposit'], Decimal)
        self.assertIsInstance(result['tenure_years'], int)
        self.assertIsInstance(result['annual_rate'], Decimal)
    
    def test_calculate_fixed_deposit_maturity_result_structure(self):
        """Test that fixed deposit maturity result has correct structure and types"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8'),
            tenure_months=12,
            payment_frequency='lump_sum'
        )
        
        # Check all required keys exist
        required_keys = ['maturity_amount', 'principal', 'interest_earned',
                        'tenure_months', 'annual_rate', 'payment_frequency']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check types
        self.assertIsInstance(result['maturity_amount'], Decimal)
        self.assertIsInstance(result['principal'], Decimal)
        self.assertIsInstance(result['interest_earned'], Decimal)
        self.assertIsInstance(result['tenure_months'], int)
        self.assertIsInstance(result['annual_rate'], Decimal)
        self.assertIsInstance(result['payment_frequency'], str)
    
    def test_calculate_loan_emi_rounding(self):
        """Test that EMI results are properly rounded"""
        result = FinancialCalculator.calculate_loan_emi(
            principal=Decimal('100000'),
            annual_rate=Decimal('12.345'),
            tenure_months=12
        )
        
        # Check that values are rounded to 2 decimal places
        self.assertEqual(str(result['emi']).split('.')[1] if '.' in str(result['emi']) else '0', 
                        str(result['emi']).split('.')[1][:2] if '.' in str(result['emi']) else '0')
        # More reliable check: rounded values should have at most 2 decimal places
        emi_str = str(result['emi'])
        if '.' in emi_str:
            decimal_places = len(emi_str.split('.')[1])
            self.assertLessEqual(decimal_places, 2)
    
    def test_calculate_savings_maturity_rounding(self):
        """Test that savings maturity results are properly rounded"""
        result = FinancialCalculator.calculate_savings_maturity(
            monthly_deposit=Decimal('5000'),
            annual_rate=Decimal('6.789'),
            tenure_years=5
        )
        
        # Check rounding
        maturity_str = str(result['maturity_amount'])
        if '.' in maturity_str:
            decimal_places = len(maturity_str.split('.')[1])
            self.assertLessEqual(decimal_places, 2)
    
    def test_calculate_fixed_deposit_maturity_rounding(self):
        """Test that fixed deposit maturity results are properly rounded"""
        result = FinancialCalculator.calculate_fixed_deposit_maturity(
            principal=Decimal('100000'),
            annual_rate=Decimal('8.456'),
            tenure_months=12,
            payment_frequency='lump_sum'
        )
        
        # Check rounding
        maturity_str = str(result['maturity_amount'])
        if '.' in maturity_str:
            decimal_places = len(maturity_str.split('.')[1])
            self.assertLessEqual(decimal_places, 2)

