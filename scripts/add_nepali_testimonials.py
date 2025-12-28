"""
Script to add demo Nepali testimonials.
Run with: python manage.py shell < scripts/add_nepali_testimonials.py
Or: python manage.py shell
Then copy-paste this code
"""

from apps.home.models import Testimonial

nepali_testimonials = [
    {
        'name': 'राम बहादुर गुरुङ',
        'position': 'सदस्य',
        'company': 'स्थानीय किसान',
        'content': 'भञ्ज्याङ सहकारीको सेवा धेरै राम्रो छ। हाम्रो पैसा सुरक्षित रहेको देखेर मन शान्त छ। सहकारीको कर्मचारीहरू धेरै मिलनसार र सहयोगी छन्।',
        'rating': 5,
        'language': 'ne',
        'is_featured': True,
        'order': 1,
        'is_active': True
    },
    {
        'name': 'सीता देवी',
        'position': 'सानो व्यापारी',
        'company': 'स्थानीय पसल',
        'content': 'भञ्ज्याङ सहकारीको ऋण सेवाले मेरो व्यापार विस्तार गर्न मद्दत गर्यो। ब्याज दर न्यायसंगत छ र प्रक्रिया पारदर्शी छ। मैले धेरै फाइदा उठाएको छु।',
        'rating': 5,
        'language': 'ne',
        'is_featured': True,
        'order': 2,
        'is_active': True
    },
    {
        'name': 'हरि प्रसाद शर्मा',
        'position': 'सदस्य',
        'company': 'शिक्षक',
        'content': 'भञ्ज्याङ सहकारीले मलाई बचत गर्न र पैसा बढाउन सिकाएको छ। उनीहरूको सेवा धेरै विश्वसनीय र पारदर्शी छ। म सदस्य बनेर धेरै खुसी छु।',
        'rating': 5,
        'language': 'ne',
        'is_featured': True,
        'order': 3,
        'is_active': True
    },
    {
        'name': 'माया थापा',
        'position': 'गृहिणी',
        'company': 'सामुदायिक सदस्य',
        'content': 'सहकारीको बचत खाताले मेरो परिवारको भविष्य सुरक्षित बनाउन मद्दत गरेको छ। कर्मचारीहरूले धेरै राम्रो व्यवहार गर्छन् र समयमै सेवा दिन्छन्।',
        'rating': 5,
        'language': 'ne',
        'is_featured': False,
        'order': 4,
        'is_active': True
    },
    {
        'name': 'कृष्ण बहादुर मगर',
        'position': 'किसान',
        'company': 'कृषि सहकारी',
        'content': 'भञ्ज्याङ सहकारीको ऋण सेवाले मेरो खेती व्यवसायमा ठूलो मद्दत गर्यो। ब्याज दर कम छ र कागजातको प्रक्रिया सजिलो छ। म धेरै खुसी छु।',
        'rating': 4,
        'language': 'ne',
        'is_featured': False,
        'order': 5,
        'is_active': True
    },
    {
        'name': 'सुनिता गुरुङ',
        'position': 'सदस्य',
        'company': 'युवा उद्यमी',
        'content': 'भञ्ज्याङ सहकारीले मलाई मेरो व्यापार सुरु गर्न मद्दत गर्यो। उनीहरूको सल्लाह र मार्गदर्शन धेरै उपयोगी थियो। अहिले मेरो व्यापार राम्रोसँग चलिरहेको छ।',
        'rating': 5,
        'language': 'ne',
        'is_featured': False,
        'order': 6,
        'is_active': True
    },
    {
        'name': 'दिल बहादुर राई',
        'position': 'सदस्य',
        'company': 'स्थानीय व्यापारी',
        'content': 'भञ्ज्याङ सहकारीको सेवा धेरै राम्रो छ। मेरो पैसा सुरक्षित रहेको देखेर मन शान्त छ। उनीहरूको कर्मचारीहरू धेरै मिलनसार र सहयोगी छन्।',
        'rating': 5,
        'language': 'ne',
        'is_featured': False,
        'order': 7,
        'is_active': True
    },
    {
        'name': 'राधा देवी',
        'position': 'सदस्य',
        'company': 'गृहिणी',
        'content': 'सहकारीको बचत खाताले मेरो परिवारको भविष्य सुरक्षित बनाउन मद्दत गरेको छ। मैले धेरै वर्षदेखि यहाँ बचत गर्दै आएको छु र धेरै खुसी छु।',
        'rating': 5,
        'language': 'ne',
        'is_featured': False,
        'order': 8,
        'is_active': True
    }
]

created_count = 0
for data in nepali_testimonials:
    testimonial, created = Testimonial.objects.get_or_create(
        name=data['name'],
        defaults=data
    )
    if created:
        created_count += 1
        print(f'Created testimonial: {testimonial.name}')
    else:
        print(f'Testimonial already exists: {testimonial.name}')

print(f'\nSuccessfully added {created_count} new Nepali testimonials!')

