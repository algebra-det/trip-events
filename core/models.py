from stay.models import Stay
from trip.models import Log, Planner, Trip
from post.models import Post
from event.models import Event

from django.db import models

from account.models import MyUser

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'uploads/profile/user_{0}/dp/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, default='uploads/profile/default.jpeg')
    website = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    following = models.ManyToManyField(MyUser, default=None, blank=True, related_name='following')
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    share_with_public = models.BooleanField(default=False)

    stay_bookmarks = models.ManyToManyField(Stay, default=None, blank=True)
    post_bookmarks = models.ManyToManyField(Post, default=None, blank=True)
    log_bookmarks = models.ManyToManyField(Log, default=None, blank=True)
    planner_bookmarks = models.ManyToManyField(Planner, default=None, blank=True)
    event_bookmarks = models.ManyToManyField(Event, default=None, blank=True)
    trip_bookmarks = models.ManyToManyField(Trip, default=None, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.phone)

    @property
    def followings(self):
        return self.following.all().count()

class BankDetails(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=120)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=10)

    def __str__(self):
        return str(self.user.phone)


BLUE_TICK_REQUEST_CHOICES = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
)


class BlueTickRequest(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    instagram = models.URLField(max_length=100)
    facebook = models.URLField(max_length=100)
    twitter = models.URLField(max_length=100)
    wikipedia = models.URLField(max_length=100)
    youtube = models.URLField(max_length=100)
    blog = models.URLField(max_length=100)
    status = models.CharField(max_length=20, choices=BLUE_TICK_REQUEST_CHOICES, default='pending')

    def __str__(self):
        return str(self.user.phone)