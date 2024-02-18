from django.contrib import admin

from .models import City, TravelType, TripInterest

admin.site.register(City)
admin.site.register(TripInterest)
admin.site.register(TravelType)
