from django.db import models
import uuid

from account.models import MyUser

def file_upload_to(instance, filename):
    return 'event/{}/{}/{}'.format(instance.user,instance.location, filename)

class TargetTrip(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_trip')
    image = models.ImageField(upload_to=file_upload_to)
    content = models.TextField()
    # Expense should be DecimalField
    expense = models.DecimalField(max_digits=10, decimal_places=2)
    video = models.FileField(upload_to=file_upload_to)
    date = models.DateField()
    location = models.CharField(max_length=50)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.user, self.date)

class Planner(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_planner')
    trip = models.ForeignKey(TargetTrip, on_delete=models.CASCADE, related_name='target_planners')
    from_location = models.CharField(max_length=50)
    from_location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    from_location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    to_location = models.CharField(max_length=50)
    to_location_longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    to_location_latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trip.title

class Expense(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_user')
    trip = models.ForeignKey(TargetTrip, on_delete=models.CASCADE, related_name='target_expense')
    expense_type = models.CharField(max_length=50)
    cost = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.trip.title


class Log(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_log')
    trip = models.ForeignKey(TargetTrip, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    note = models.TextField()
    pic = models.ImageField(upload_to=file_upload_to)
    video = models.ImageField(upload_to=file_upload_to)
    date = models.DateTimeField(auto_now_add=True)
    expense = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=50)
    public = models.BooleanField(default=False)
    likes = models.ManyToManyField(MyUser, default=None, blank=True, related_name='target_likes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_comments')
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.log.trip, self.user)


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='target_book')
    trip = models.ForeignKey(TargetTrip, on_delete=models.CASCADE)
    members = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.target_event, self.user)

    class Meta:
        verbose_name_plural = "Bookings"