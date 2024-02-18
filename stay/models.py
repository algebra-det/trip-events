from typing import Optional
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone

import uuid
from account.models import MyUser
from trip.models import Planner

def file_upload_to(instance, filename):
    return 'stay/{}/{}/{}'.format(instance.stay.user,instance.stay.title, filename)

def facility_pic_upload_to(instance, filename):
    return 'facilities/{}/{}'.format(instance.title, filename)


STAY_STATUS_CHOICES = (
    ('Active', 'Active'),
    ('InActive', 'InActive'),
)

STAY_TYPE_CHOICES = (
    ('Home Stay', 'Home Stay'),
    ('Hostel', 'Hostel'),
    ('Camp Site', 'Camp Site'),
    ('GLAMPING', 'GLAMPING'),
    ('OffBeat', 'OffBeat'),
    ('TreeHouse', 'TreeHouse'),
    ('House Boats', 'House Boats'),
    ('Farm Stay', 'Farm Stay'),
    ('Tiny House', 'Tiny House'),
    ('Others', 'Others'),
)

class Facility(models.Model):
    title = models.CharField(max_length=20)
    image = models.ImageField(upload_to=facility_pic_upload_to, default='facilities/default.jpeg')

    def __str__(self):
        return self.title

class Stay(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    stay_type = models.CharField(max_length=50, choices=STAY_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    facilities = models.ManyToManyField(Facility, default=None, blank=True, related_name='stays')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STAY_STATUS_CHOICES, default='Active')

    # max_people_allowed = models.PositiveIntegerField()
    max_guests_allowed = models.PositiveIntegerField()
    extra_mattress_available = models.BooleanField(default=False)
    price_per_extra_mattress = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    number_of_extra_mattress_available = models.PositiveIntegerField(null=True, blank=True)

    pet_friendly = models.BooleanField(blank=True, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.title, self.location)

class StayImage(models.Model):
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=file_upload_to)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.stay.title

class NearestHotSpots(models.Model):
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name="nearby")
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


BOOKING_STATUS_OPTIONS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
    ('Cancelled By Host', 'Cancelled By Host'),
    ('Cancelled By User', 'Cancelled By User'),
)

class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='stay_book')
    planner = models.ForeignKey(Planner, on_delete=models.SET_NULL, null=True, blank=True)
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE)
    price_of_stay = models.PositiveIntegerField()
    paid_amount = models.PositiveIntegerField()
    number_of_adults = models.IntegerField()
    number_of_children = models.IntegerField(blank=True, default=0)
    extra_mattress = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_OPTIONS, default="Pending")
    paid = models.BooleanField(default=False)
    cancellation_date = models.DateTimeField(blank=True, null=True)
    commission_at_time_of_booking = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.stay, self.user)
    
    @property
    def guests(self):
        return int(self.number_of_adults + self.number_of_children)

    class Meta:
        verbose_name_plural = "Bookings"

    def save(self, *args, **kwargs):
        if self.status == 'Cancelled By Host' or self.status == 'Cancelled By User':
            self.cancellation_date = timezone.now()
        else:
            self.cancellation_date = None
        return super(Booking, self).save(*args, **kwargs)

class PlannerWishlist(models.Model):
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE, related_name='stay_wishlsit')
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.planner} - {self.stay}'

RATING_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class Review(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.booking.user.phone, self.booking.stay)

