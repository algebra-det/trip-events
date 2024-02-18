from django.db import models
from django.utils import timezone

def interest_upload_to(instance, filename):
    # return 'trip_interest/{}/{}'.format(instance.title, filename+ "___" +str(timezone.now()))
    return 'trip_interest/{}/{}'.format(instance.title, filename)

def type_upload_to(instance, filename):
    return 'trip_type/{}/{}'.format(instance.title, filename)

def city_upload_to(instance, filename):
    return 'trip_type/{}/{}'.format(instance.title, filename)

class City(models.Model):
    title = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    image = models.ImageField(upload_to=city_upload_to)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TripInterest(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to=interest_upload_to)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TravelType(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to=type_upload_to)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title