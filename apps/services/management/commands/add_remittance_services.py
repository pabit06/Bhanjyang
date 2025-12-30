from django.core.management.base import BaseCommand
from apps.services.models import RemittanceService, DigitalService


class Command(BaseCommand):
    help = 'Add specific remittance and digital services (IME, CFS, City Express, Western Union, eSewa, Khalti)'

    def handle(self, *args, **options):
        self.stdout.write('Adding remittance and digital services...')
        
        # International Remittance Services
        remittance_services = [
            {
                'service_type': 'international',
                'english_name': 'IME Remittance',
                'nepali_name': 'आईएमई रिमिटेन्स',
                'description': 'IME Remit is Nepal\'s No. 1 remittance company with 25+ years of experience. Trusted by millions, IME has been playing a crucial role in safely facilitating remittance transfers. Our partnerships with international remittance companies enable our clients to send and receive money worldwide—quickly, safely, and efficiently. With 150K+ global locations in 200+ countries, IME ensures seamless money transfers wherever you are.',
                'processing_time': 'Instant to few minutes',
                'fees': 'Competitive rates with best exchange rates. Zero extra fee for receiving in Khalti by IME wallet.',
                'icon': 'fas fa-globe-americas',
                'color': 'rupablue',
                'is_featured': True,
                'is_active': True
            },
            {
                'service_type': 'international',
                'english_name': 'CFS',
                'nepali_name': 'सीएफएस',
                'slug': 'himalremit',  # Custom slug for URL
                'description': 'HimalRemit™, a premium online customer focused and technology oriented Money Transfer product, is brought to you by Himalayan Bank Limited - the leading joint venture bank of Nepal. CFS is the Principal Agent for HimalRemit™, offering secure and reliable remittance services with competitive rates. Himalayan Bank is a pioneer in the field of retail money transfer business with almost two decades long customized service delivery experience.',
                'processing_time': '1-3 hours',
                'fees': 'Competitive rates. See detailed charges for each country.',
                'icon': 'fas fa-mountain',
                'color': 'rupablue',
                'is_featured': True,
                'is_active': True
            },
            {
                'service_type': 'international',
                'english_name': 'City Express',
                'nepali_name': 'सिटी एक्सप्रेस',
                'description': 'City Express Money Transfer offers a quick, reliable, and secure way to send money to anyone in Nepal. With 18+ years of experience, 5M+ customers served, and 25,000+ payout locations across Nepal, City Express is one of Nepal\'s leading remittance companies. Licensed by Nepal Rastra Bank, we partner with world\'s top money transfer companies to facilitate seamless remittance services.',
                'processing_time': 'Instant to few minutes',
                'fees': 'Best exchange rates and lowest charges. Competitive rates based on amount and destination.',
                'icon': 'fas fa-shipping-fast',
                'color': 'rupablue',
                'is_featured': True,
                'is_active': True
            },
            {
                'service_type': 'international',
                'english_name': 'Western Union',
                'nepali_name': 'वेस्टर्न युनियन',
                'description': 'Global remittance service provider, one of the most trusted names in international money transfers.',
                'processing_time': 'Instant to 1 hour',
                'fees': 'Varies by amount and destination country',
                'icon': 'fas fa-globe',
                'color': 'rupablue',
                'is_featured': True,
                'is_active': True
            },
        ]
        
        # Digital Services (E-Wallets)
        digital_services = [
            {
                'service_type': 'e_wallet',
                'english_name': 'eSewa',
                'nepali_name': 'ईसेवा',
                'description': 'Nepal\'s leading digital wallet and payment service. Use eSewa for mobile top-ups, bill payments, online shopping, and money transfers.',
                'features': '• Mobile top-up\n• Bill payments (electricity, water, internet, TV)\n• Online shopping\n• Money transfer\n• QR code payments\n• Bank transfers',
                'requirements': '• Valid mobile number\n• eSewa account\n• Internet connection',
                'fees': 'Free for most services, minimal charges for some transactions',
                'icon': 'fas fa-mobile-alt',
                'color': 'deuraligreen',
                'is_featured': True,
                'is_active': True
            },
            {
                'service_type': 'e_wallet',
                'english_name': 'Khalti',
                'nepali_name': 'खल्ती',
                'description': 'Popular digital wallet in Nepal for seamless digital payments, bill payments, and money transfers.',
                'features': '• Mobile top-up\n• Bill payments\n• Online shopping\n• Money transfer\n• QR code payments\n• Movie tickets\n• Flight bookings',
                'requirements': '• Valid mobile number\n• Khalti account\n• Internet connection',
                'fees': 'Free for most services, minimal charges for some transactions',
                'icon': 'fas fa-wallet',
                'color': 'deuraligreen',
                'is_featured': True,
                'is_active': True
            },
        ]
        
        # Add Remittance Services
        for data in remittance_services:
            # Check by slug first if provided, otherwise by english_name
            lookup_field = 'slug' if 'slug' in data else 'english_name'
            lookup_value = data.get('slug') or data['english_name']
            
            service = RemittanceService.objects.filter(**{lookup_field: lookup_value}).first()
            
            if service:
                # Update existing service
                for key, value in data.items():
                    setattr(service, key, value)
                service.save()
                self.stdout.write(self.style.WARNING(f'Updated: {data["english_name"]} (slug: {service.slug})'))
            else:
                # Create new service
                service = RemittanceService.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f'Created: {data["english_name"]} (slug: {service.slug})'))
        
        # Add Digital Services
        for data in digital_services:
            service, created = DigitalService.objects.get_or_create(
                english_name=data['english_name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {data["english_name"]}'))
            else:
                # Update existing service
                for key, value in data.items():
                    setattr(service, key, value)
                service.save()
                self.stdout.write(self.style.WARNING(f'Updated: {data["english_name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll services added successfully!'))

