from django.core.management.base import BaseCommand
from services.models import SavingsAccount, FixedDeposit, LoanType, RemittanceService, MemberRelief


class Command(BaseCommand):
    help = 'Populate the database with comprehensive service data'

    def handle(self, *args, **options):
        self.stdout.write('Populating comprehensive services data...')
        
        # Create Enhanced Savings Accounts
        savings_data = [
            {
                'account_type': 'general',
                'nepali_name': 'साधारण बचत',
                'english_name': 'General Savings',
                'interest_rate': 5.00,
                'minimum_balance': 1000.00,
                'description': 'Basic savings account for daily banking needs with easy access to funds.',
                'features': '• No minimum balance requirement\n• Free passbook\n• Online banking access\n• ATM card facility\n• Mobile banking',
                'icon': 'fas fa-piggy-bank',
                'color': 'deuraligreen',
                'is_featured': True
            },
            {
                'account_type': 'child',
                'nepali_name': 'बाल बचत',
                'english_name': 'Child Savings',
                'interest_rate': 6.00,
                'minimum_balance': 500.00,
                'description': 'Special savings account for children to encourage saving habits from early age.',
                'features': '• Higher interest rate for children\n• Educational materials\n• Parental guidance\n• Birthday bonuses\n• Savings competitions',
                'icon': 'fas fa-child',
                'color': 'bhanjyangred',
                'is_featured': True
            },
            {
                'account_type': 'senior_citizen',
                'nepali_name': 'जेष्ठ नागरिक बचत',
                'english_name': 'Senior Citizen Savings',
                'interest_rate': 6.00,
                'minimum_balance': 2000.00,
                'description': 'Preferential savings account for senior citizens with additional benefits.',
                'features': '• Higher interest rates\n• Priority customer service\n• Home banking services\n• Health check-up benefits\n• Special events',
                'icon': 'fas fa-user-tie',
                'color': 'deuraligreen',
                'is_featured': False
            },
            {
                'account_type': 'monthly',
                'nepali_name': 'मासिक बचत',
                'english_name': 'Monthly Savings',
                'interest_rate': 8.00,
                'minimum_balance': 5000.00,
                'description': 'Monthly savings scheme with highest interest rates for disciplined savers.',
                'features': '• Highest interest rate\n• Monthly deposit requirement\n• Bonus on completion\n• Goal-oriented saving\n• Financial planning support',
                'icon': 'fas fa-calendar-alt',
                'color': 'bhanjyangred',
                'is_featured': True
            },
            {
                'account_type': 'daily',
                'nepali_name': 'दैनिक बचत',
                'english_name': 'Daily Savings',
                'interest_rate': 5.00,
                'minimum_balance': 100.00,
                'description': 'Savings account with daily interest calculation for frequent depositors.',
                'features': '• Daily interest calculation\n• Low minimum balance\n• Unlimited transactions\n• Quick access\n• Mobile app support',
                'icon': 'fas fa-calendar-day',
                'color': 'deuraligreen',
                'is_featured': False
            },
            {
                'account_type': 'institutional',
                'nepali_name': 'संस्थागत बचत',
                'english_name': 'Institutional Savings',
                'interest_rate': 4.00,
                'minimum_balance': 10000.00,
                'description': 'Savings account for institutions and organizations with bulk transaction support.',
                'features': '• Bulk transaction support\n• Corporate banking\n• Dedicated relationship manager\n• Business tools\n• Reporting features',
                'icon': 'fas fa-building',
                'color': 'deuraligreen',
                'is_featured': False
            }
        ]
        
        for data in savings_data:
            SavingsAccount.objects.get_or_create(
                account_type=data['account_type'],
                defaults=data
            )
            self.stdout.write(f"Created/Updated: {data['english_name']} ({data['interest_rate']}%)")
        
        # Create Enhanced Fixed Deposits
        fixed_deposit_data = [
            {'duration_months': 3, 'payment_frequency': 'lump_sum', 'interest_rate': 5.25, 'minimum_amount': 10000, 'maximum_amount': 1000000, 'description': 'Short-term fixed deposit for quick returns', 'benefits': '• Quick returns\n• Flexible amounts\n• Easy liquidity'},
            {'duration_months': 6, 'payment_frequency': 'monthly', 'interest_rate': 5.50, 'minimum_amount': 25000, 'maximum_amount': 2000000, 'description': 'Medium-term deposit with monthly interest payments', 'benefits': '• Regular income\n• Competitive rates\n• Flexible terms'},
            {'duration_months': 6, 'payment_frequency': 'quarterly', 'interest_rate': 5.75, 'minimum_amount': 25000, 'maximum_amount': 2000000, 'description': 'Quarterly interest payment option for better cash flow', 'benefits': '• Quarterly income\n• Higher rates\n• Better cash flow'},
            {'duration_months': 6, 'payment_frequency': 'lump_sum', 'interest_rate': 6.00, 'minimum_amount': 25000, 'maximum_amount': 2000000, 'description': 'Lump sum payment option for maximum returns', 'benefits': '• Maximum returns\n• Compound interest\n• Long-term growth'},
            {'duration_months': 12, 'payment_frequency': 'monthly', 'interest_rate': 6.25, 'minimum_amount': 50000, 'maximum_amount': 5000000, 'description': 'Annual deposit with monthly interest payments', 'benefits': '• Monthly income\n• Higher rates\n• Stable returns'},
            {'duration_months': 12, 'payment_frequency': 'quarterly', 'interest_rate': 6.50, 'minimum_amount': 50000, 'maximum_amount': 5000000, 'description': 'Quarterly interest payments for annual deposits', 'benefits': '• Quarterly income\n• Competitive rates\n• Annual planning'},
            {'duration_months': 12, 'payment_frequency': 'lump_sum', 'interest_rate': 7.00, 'minimum_amount': 50000, 'maximum_amount': 5000000, 'description': 'Best annual rate for maximum returns', 'benefits': '• Best rates\n• Maximum returns\n• Long-term planning'},
        ]
        
        for data in fixed_deposit_data:
            FixedDeposit.objects.get_or_create(
                duration_months=data['duration_months'],
                payment_frequency=data['payment_frequency'],
                defaults=data
            )
            self.stdout.write(f"Created/Updated: {data['duration_months']} months - {data['payment_frequency']} ({data['interest_rate']}%)")
        
        # Create Enhanced Loan Types
        loan_data = [
            {
                'loan_category': 'business',
                'nepali_name': 'व्यवसाय ऋण',
                'english_name': 'Business Loan',
                'monthly_installment_rate': 12.5,
                'quarterly_installment_rate': 13.0,
                'monthly_interest_rate': 15.0,
                'minimum_amount': 100000,
                'maximum_amount': 5000000,
                'max_tenure_years': 5,
                'description': 'Comprehensive business loans for expansion, working capital, and business development.',
                'requirements': '• Business registration\n• Financial statements\n• Business plan\n• Collateral security\n• Income proof',
                'benefits': '• Quick approval\n• Flexible terms\n• Business support\n• Technical assistance\n• Networking opportunities',
                'icon': 'fas fa-briefcase',
                'color': 'deuraligreen',
                'is_featured': True
            },
            {
                'loan_category': 'agricultural',
                'nepali_name': 'कृषि ऋण',
                'english_name': 'Agricultural Loan',
                'monthly_installment_rate': 10.5,
                'quarterly_installment_rate': 11.0,
                'monthly_interest_rate': 13.0,
                'minimum_amount': 50000,
                'maximum_amount': 2000000,
                'max_tenure_years': 7,
                'description': 'Special loans for farmers and agricultural activities with seasonal payment options.',
                'requirements': '• Land ownership\n• Farming experience\n• Crop plan\n• Agricultural training\n• Seasonal income proof',
                'benefits': '• Lower interest rates\n• Seasonal payments\n• Agricultural support\n• Training programs\n• Market access',
                'icon': 'fas fa-seedling',
                'color': 'bhanjyangred',
                'is_featured': True
            },
            {
                'loan_category': 'house_construction',
                'nepali_name': 'घर निर्माण ऋण',
                'english_name': 'House Construction Loan',
                'monthly_installment_rate': 12.5,
                'quarterly_installment_rate': 13.0,
                'monthly_interest_rate': 15.0,
                'minimum_amount': 500000,
                'maximum_amount': 10000000,
                'max_tenure_years': 15,
                'description': 'Long-term loans for house construction and renovation with flexible payment options.',
                'requirements': '• Land ownership\n• Construction plan\n• Building permit\n• Collateral security\n• Income stability',
                'benefits': '• Long-term planning\n• Construction support\n• Technical guidance\n• Insurance coverage\n• Home improvement',
                'icon': 'fas fa-home',
                'color': 'deuraligreen',
                'is_featured': False
            },
            {
                'loan_category': 'vehicle',
                'nepali_name': 'सवारी खरिद ऋण',
                'english_name': 'Vehicle Purchase Loan',
                'monthly_installment_rate': 12.5,
                'quarterly_installment_rate': 13.0,
                'monthly_interest_rate': 15.0,
                'minimum_amount': 200000,
                'maximum_amount': 3000000,
                'max_tenure_years': 5,
                'description': 'Loans for purchasing vehicles and transportation with competitive rates.',
                'requirements': '• Driver license\n• Vehicle details\n• Down payment\n• Income proof\n• Insurance coverage',
                'benefits': '• Quick processing\n• Vehicle support\n• Insurance benefits\n• Maintenance support\n• Resale guidance',
                'icon': 'fas fa-car',
                'color': 'bhanjyangred',
                'is_featured': False
            },
            {
                'loan_category': 'education',
                'nepali_name': 'शिक्षा ऋण',
                'english_name': 'Education Loan',
                'monthly_installment_rate': 11.0,
                'quarterly_installment_rate': 11.5,
                'monthly_interest_rate': 13.5,
                'minimum_amount': 100000,
                'maximum_amount': 2000000,
                'max_tenure_years': 8,
                'description': 'Special loans for education with deferred payment options until course completion.',
                'requirements': '• Admission letter\n• Course details\n• Academic records\n• Guarantor\n• Future income potential',
                'benefits': '• Deferred payments\n• Lower rates\n• Career support\n• Internship opportunities\n• Job placement',
                'icon': 'fas fa-graduation-cap',
                'color': 'deuraligreen',
                'is_featured': False
            }
        ]
        
        for data in loan_data:
            LoanType.objects.get_or_create(
                loan_category=data['loan_category'],
                defaults=data
            )
            self.stdout.write(f"Created/Updated: {data['english_name']}")
        
        # Create Enhanced Remittance Services
        remittance_data = [
            {
                'service_type': 'domestic',
                'name': 'Domestic Transfers',
                'description': 'Fast and secure money transfers within Nepal with instant processing.',
                'features': '• Instant transfers\n• Low fees\n• Wide network coverage\n• Mobile app support\n• SMS notifications',
                'transfer_limit_min': 100,
                'transfer_limit_max': 100000,
                'processing_time': 'Instant to 2 hours',
                'fees': 'Minimal charges: NPR 10-50 based on amount'
            },
            {
                'service_type': 'international',
                'name': 'International Remittance',
                'description': 'Reliable services for sending money from abroad with competitive rates.',
                'features': '• Global network\n• Competitive rates\n• Secure transfers\n• Multiple currencies\n• 24/7 support',
                'transfer_limit_min': 1000,
                'transfer_limit_max': 1000000,
                'processing_time': '1-3 business days',
                'fees': 'Competitive international rates: 0.5-2% of transfer amount'
            },
            {
                'service_type': 'mobile_banking',
                'name': 'Mobile Banking',
                'description': '24/7 access to your accounts and services through mobile application.',
                'features': '• Account balance\n• Fund transfers\n• Bill payments\n• Mobile app\n• QR payments',
                'transfer_limit_min': 100,
                'transfer_limit_max': 50000,
                'processing_time': 'Real-time',
                'fees': 'Free for basic services, minimal charges for premium features'
            }
        ]
        
        for data in remittance_data:
            RemittanceService.objects.get_or_create(
                service_type=data['service_type'],
                defaults=data
            )
            self.stdout.write(f"Created/Updated: {data['name']}")
        
        # Create Member Relief Programs
        relief_data = [
            {
                'relief_type': 'medical',
                'title': 'Medical Emergency Relief Fund',
                'nepali_title': 'चिकित्सा आपत्कालीन राहत कोष',
                'description': 'Financial assistance for members facing medical emergencies and health crises.',
                'eligibility': '• Active member for minimum 2 years\n• Medical emergency documentation\n• Income below threshold\n• No existing medical insurance',
                'benefits': '• Up to NPR 100,000 assistance\n• Medical consultation support\n• Hospital coordination\n• Follow-up care',
                'application_process': '1. Submit application with medical documents\n2. Committee review within 48 hours\n3. Approval and disbursement\n4. Regular follow-up',
                'required_documents': '• Medical reports\n• Hospital bills\n• Income certificate\n• Member ID\n• Emergency contact',
                'contact_info': 'Contact: Medical Relief Committee\nPhone: +977-9856083101\nEmail: medical@bhanjyang.coop.np',
                'icon': 'fas fa-heartbeat',
                'color': 'bhanjyangred'
            },
            {
                'relief_type': 'education',
                'title': 'Educational Support Program',
                'nepali_title': 'शैक्षिक सहयोग कार्यक्रम',
                'description': 'Support for member families to ensure children receive quality education.',
                'eligibility': '• Member children aged 5-18\n• Good academic performance\n• Family income below threshold\n• Regular member for 3+ years',
                'benefits': '• School fee assistance\n• Educational materials\n• Tutoring support\n• Career guidance\n• Scholarship opportunities',
                'application_process': '1. Submit academic records\n2. Family income verification\n3. Committee interview\n4. Annual renewal',
                'required_documents': '• Academic transcripts\n• Income certificate\n• School fee receipts\n• Family photos\n• Recommendation letters',
                'contact_info': 'Contact: Education Support Committee\nPhone: +977-9856083101\nEmail: education@bhanjyang.coop.np',
                'icon': 'fas fa-graduation-cap',
                'color': 'deuraligreen'
            },
            {
                'relief_type': 'disaster',
                'title': 'Natural Disaster Relief',
                'nepali_title': 'प्राकृतिक आपदा राहत',
                'description': 'Immediate assistance for members affected by natural disasters and calamities.',
                'eligibility': '• All active members\n• Disaster-affected area resident\n• Loss documentation\n• Immediate need verification',
                'benefits': '• Emergency cash assistance\n• Temporary shelter support\n• Food and clothing\n• Recovery planning\n• Insurance guidance',
                'application_process': '1. Immediate assessment\n2. Quick approval\n3. Emergency disbursement\n4. Recovery support',
                'required_documents': '• Disaster report\n• Loss assessment\n• Identity proof\n• Damage photos\n• Local authority verification',
                'contact_info': 'Contact: Disaster Relief Team\nPhone: +977-9856083101\nEmail: disaster@bhanjyang.coop.np',
                'icon': 'fas fa-shield-alt',
                'color': 'bhanjyangred'
            },
            {
                'relief_type': 'welfare',
                'title': 'Member Welfare Support',
                'nepali_title': 'सदस्य कल्याण सहयोग',
                'description': 'Comprehensive welfare support for members in need of social assistance.',
                'eligibility': '• Long-term members (5+ years)\n• Demonstrated need\n• Community recommendation\n• Regular participation',
                'benefits': '• Monthly assistance\n• Skill development\n• Job placement\n• Social integration\n• Long-term support',
                'application_process': '1. Community recommendation\n2. Need assessment\n3. Committee approval\n4. Regular monitoring',
                'required_documents': '• Community recommendation\n• Need assessment report\n• Income verification\n• Family details\n• Support plan',
                'contact_info': 'Contact: Welfare Committee\nPhone: +977-9856083101\nEmail: welfare@bhanjyang.coop.np',
                'icon': 'fas fa-hands-helping',
                'color': 'deuraligreen'
            }
        ]
        
        for data in relief_data:
            MemberRelief.objects.get_or_create(
                relief_type=data['relief_type'],
                title=data['title'],
                defaults=data
            )
            self.stdout.write(f"Created/Updated: {data['title']}")
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated comprehensive services data!')
        )
