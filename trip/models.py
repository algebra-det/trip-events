from django.db import models
import uuid

from django.db.models.base import ModelState

from account.models import MyUser
from account.models import TravelType
# from stay.models import Stay
# from event.models import Event

def file_upload_to(instance, filename):
    return 'log_files/{}/{}/{}'.format(instance.log.trip.title,instance.log.user.id, filename)

def trip_video_upload_to(instance, filename):
    return 'trip_video/{}/{}/{}'.format(instance.trip.title,instance.log.user.id, filename)


TRIP_TYPES = (
    ('Incomplete', 'Incomplete'),
    ('Future', 'Future'),
    ('On-Going', 'On-Going'),
    ('Past', 'Past'),
)

TYPE_OF_TRIP_CHOICES = (
    # ('Solo', 'Solo'),
    # ('Family', 'Family'),
    # ('Friends', 'Friends'),
    ('Private', 'Private'),
    ('Public', 'Public'),
)

class Trip(models.Model):
    creator = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='created_trips')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    type_of_travel= models.CharField(max_length=50, choices=TYPE_OF_TRIP_CHOICES)
    trip_type  = models.ForeignKey(TravelType, on_delete=models.SET_NULL, null=True)
    members = models.ManyToManyField(MyUser, default=None, blank=True, related_name='members')
    number_of_travellers = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    by_admin = models.BooleanField(default=False)

    incomplete = models.BooleanField(default=True)
    

    # Fields for Target Trips/ Bucket List
    content = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    booking_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.title, self.user)

    @property
    def number_of_members(self):
        return self.members.all().count()

class TripVideos(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_videos')
    trip_video = models.FileField(upload_to=trip_video_upload_to)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trip


class TripLikes(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='trip_liked')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.trip, self.user)

# Comments For Trip when it gets Posted
class TripComment(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='trip_comments')
    text = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.post.id, self.user.name)


class Planner(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='planners')
    from_location = models.CharField(max_length=50)
    from_location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    from_location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    to_location = models.CharField(max_length=50)
    to_location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    to_location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField()
    stay_budget = models.IntegerField(null=True, blank=True)
    activity_budget = models.IntegerField(null=True, blank=True)
    event_budget = models.IntegerField(null=True, blank=True)
    transport_budget = models.IntegerField(null=True, blank=True)
    # stay_wishlist = models.ManyToManyField(Stay, on_delete=models.CASCADE)
    # event_wishlist = models.ManyToManyField(Event, on_delete=models.CASCADE)
    activities_requested = models.BooleanField(default=False)
    transport_requested = models.BooleanField(default=False)

    public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trip.title


class PlannerLikes(models.Model):
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='planner_liked')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.planner.trip, self.user)


# Comments For Planner when it gets Posted
class PlannerComment(models.Model):
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='planner_comments')
    text = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.post.id, self.user.name)

class ExpenseType(models.Model):
    title = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Expense(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trip.title


class Log(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    note = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=50)
    public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class LogFiles(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    log_file = models.ImageField(upload_to=file_upload_to)

    def __str__(self):
        return self.log.trip

class LogLikes(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='log_liked')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.log, self.user)


# Comments for Trip Logs
class LogComment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='log_comments')
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.log.trip, self.user)


class Request(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='trip_request')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.trip, self.user)


class Booking(models.Model):
    booking_id = models.CharField(default=uuid.uuid4, editable=False, max_length=100)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='trip_bookings')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    members = models.IntegerField()
    price_of_trip = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.target_event, self.user)

    class Meta:
        verbose_name_plural = "Bookings"


class MemberUser(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='member_user')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    requested_date = models.DateTimeField(auto_now_add=True)
    joined_date = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    
    def __str__(self):
        return '{} - {}'.format(self.user, self.trip)