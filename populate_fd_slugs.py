import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.services.models import FixedDeposit

def populate_slugs():
    fds = FixedDeposit.objects.all()
    count = 0
    for fd in fds:
        if not fd.slug:
            # Generate a unique slug based on ID and duration
            base_name = f"Fixed Deposit {fd.duration_months} Months - {fd.payment_frequency}"
            slug = slugify(base_name)
            # Ensure uniqueness just in case (though combo should be unique)
            if FixedDeposit.objects.filter(slug=slug).exists():
                slug = f"{slug}-{fd.id}"
            
            fd.slug = slug
            fd.english_name = f"Fixed Deposit ({fd.duration_months} Months)"
            fd.nepali_name = f"मुद्दती निक्षेप ({fd.duration_months} महिना)"
            fd.save()
            count += 1
            print(f"Updated FD {fd.id} with slug: {slug}")
    print(f"Successfully populated slugs for {count} records.")

if __name__ == "__main__":
    populate_slugs()
