from stay.models import Stay, Facility

def save_facilities(facilities, stay_id):
    stay = Stay.objects.get(id=stay_id)
    if stay.facilities.all().count():
        stay.facilities.set([])

    for item in facilities:
        if facility := Facility.objects.filter(title=item):
            if facility.first() not in stay.facilities.all():
                stay.facilities.add(facility.first())