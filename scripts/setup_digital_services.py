from apps.services.models import DigitalService
from django.core.files import File
import os

def run():
    # 1. Ensure Mobile Banking Exists
    mobile_banking, created = DigitalService.objects.get_or_create(
        english_name="Mobile Banking",
        defaults={
            "nepali_name": "मोबाइल बैंकिङ्ग",
            "service_type": "mobile_banking",
            "description": "Bhanjyang Smart App is our official mobile banking application. Check balances, transfer funds, pay bills, and more directly from your smartphone.",
            "features": "Balance Enquiry\nMini Statement\nFund Transfer\nBill Payments (Electricity, Water, Internet)\nMobile Top-up\nQR Payment",
            "requirements": "Membership Account\nValid ID\nMobile Number registered with the cooperative",
            "fees": "Registration Fee: NPR 100\nYearly Renewal: NPR 100",
            "is_featured": True,
            "is_active": True,
            "icon": "fas fa-mobile-alt",
            "color": "deuraligreen"
        }
    )
    if created:
        print("Created Mobile Banking service.")
    else:
        print("Mobile Banking service already exists. Updating to be featured.")
        mobile_banking.is_featured = True
        mobile_banking.nepali_name = "मोबाइल बैंकिङ्ग"
        mobile_banking.save()

    # 2. Check for Khalti and eSewa and update them (or create if missing for demo)
    # The user said they ARE there, so we expect to find them.
    # If they are there, we might want to make them NOT featured or categorize them as "Wallets"
    
    wallets = ["Khalti", "eSewa", "IME Pay", "Prabhu Pay"]
    for wallet_name in wallets:
        try:
            wallet = DigitalService.objects.get(english_name__icontains=wallet_name)
            print(f"Found {wallet.english_name}. Updating category/icon...")
            wallet.service_type = "e_wallet" # Ensure they are wallets
            wallet.is_featured = False # Mobile banking should be the star
            wallet.save()
        except DigitalService.DoesNotExist:
            print(f"{wallet_name} not found (that's okay, maybe specific logic handles them).")

if __name__ == "__main__":
    run()
