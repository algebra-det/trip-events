from django.db import models
from django.db.models import Q, Sum

import uuid

from django.db.models.fields.related import OneToOneField

from account.models import MyUser
from trip.models import Planner

def file_upload_to(instance, filename):
    return 'event/{}/{}/{}'.format(instance.event.user,instance.event.location, filename)

EVENT_TYPE_CHOICES = (
    ('Live Screening', 'Live Screening'),
    ('InHouse Gathering', 'InHouse Gathering'),
    ('Concert', 'Concert'),
    ('Sports', 'Sports'),
    ('Party', 'Party'),
    ('Bon-Fire', 'Bon-Fire'),
    ('Open Field', 'Open Field'),
)

EVENT_STATUS_CHOICES = (
    ('Active', 'Active'),
    ('InActive', 'InActive'),
)
class Event(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    content = models.TextField()
    adult_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    child_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stag_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    couple_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eves_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission = models.PositiveIntegerField()
    location = models.CharField(max_length=200)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    seats = models.IntegerField()
    people_interested = models.ManyToManyField(MyUser, default=None, blank=True, related_name='event_interested_people')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='Active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.title, self.location)
    
    @property
    def available_seats(self):
        response = Booking.objects.filter(Q(event__id=self.id) & Q(paid=True) & (Q(status='Approved') | Q(status='Pending'))).aggregate(Sum('members'))
        return self.seats - (response['members__sum'] or 0)


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=file_upload_to)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event.title



BOOKING_STATUS_OPTIONS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
    ('Cancelled By Host', 'Cancelled By Host'),
    ('Cancelled By User', 'Cancelled By User'),
)

class Booking(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='event_book')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    planner = models.ForeignKey(Planner, on_delete=models.SET_NULL, null=True, blank=True, related_name='event_planner')
    members = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_OPTIONS, default='Pending')
    paid = models.BooleanField(default=False)
    number_of_adults = models.IntegerField(default=0, blank=True, null=True)
    number_of_child = models.IntegerField(default=0, blank=True, null=True)
    number_of_stag = models.IntegerField(default=0, blank=True, null=True)
    number_of_couple = models.IntegerField(default=0, blank=True, null=True)
    number_of_eves = models.IntegerField(default=0, blank=True, null=True)
    adult_entry_cost = models.DecimalField(max_digits=10, decimal_places=2)
    child_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stag_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    couple_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eves_entry_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_at_time_of_booking = models.PositiveIntegerField()

    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.event.title, self.user)

    class Meta:
        verbose_name_plural = "Bookings"
    
    # @property
    # def members(self):
    #     return int(
    #         self.number_of_adults +
    #         self.number_of_child +
    #         self.number_of_couple +
    #         self.number_of_eves +
    #         self.number_of_eves
    #     )

    def save(self, *args, **kwargs):
        self.members = int(
            self.number_of_adults +
            self.number_of_child +
            self.number_of_couple +
            self.number_of_eves +
            self.number_of_eves
        )
        return super(Booking, self).save(*args, **kwargs)



class PlannerWishlist(models.Model):
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE, related_name='event_wishlsit')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.planner} - {self.event}'

RATING_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class Review(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='event_reviews')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.user.phone, self.booking.event)

