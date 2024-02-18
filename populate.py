import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'migo.settings')
django.setup()

from stay.models import Facility

facilities = [
    'WiFi',
    'Breakfast',
    'Parking',
    'Play Area',
    'Hot-Cold Water',
    'Air Conditioner',
    'Balcony',
    'CareTaker',
    'Lounge',
    'Swimming Pool',
    'Child Play Area',
    'Day Care',
    'Others'
]

def populate_facilities():
    for item in facilities:
        print('Facility: ', item)
        if not Facility.objects.filter(title=item).exists():
            facility = Facility()
            facility.title = item
            facility.save()
            print('____________________\n')
        else:
            print('Already There____________________\n')


populate_facilities()
print("Populating Completed!")
