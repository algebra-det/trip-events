import json
from rest_framework import serializers
from stay.api.serializers import NearestHotSpotsSerializer
import requests, os
from stay.models import NearestHotSpots, Stay


def save_nearby_from_google_api(stay_id):
    stay = Stay.objects.get(id=stay_id)
    stay_location = stay.location
    stay_location = stay_location.replace(" ", "%20")
    url = """https://maps.googleapis.com/maps/api/place/findplacefromtext/json?
                input={}&
                inputtype=textquery&
                fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&
                key={}""".format(stay_location, os.environ.get('GOOGLE_MAP_API_KEY'))
    print(url)

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    response = response.json()
    print(type(response), response)

    locations = response['candidates']
    print(len(locations))
    
    nearby_locations = []
    if response['status'] == 'OK' and len(locations):
        for item in locations:
            place = NearestHotSpots.objects.create(stay=stay, title=item['name'])
            place.save()
            serializer = NearestHotSpotsSerializer(place)
            nearby_locations.append(serializer.data)
    
    return nearby_locations
