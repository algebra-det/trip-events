from .models import Trip, Planner
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.conf import settings

@receiver(post_save, sender=Trip)
def change_trip_type(sender, instance, created, **kwargs):
    post_save.disconnect(change_trip_type, sender=sender)
    planners = instance.planners.all()
    if planners.exists():
        instance.incomplete = False
        instance.save()
    post_save.connect(change_trip_type, sender=sender)
post_save.connect(change_trip_type, sender= Trip)


@receiver(pre_delete, sender=Planner)
def check_if_trips_planners_are_None(sender, instance, **kwargs):
    instance.trip.save()

@receiver(post_save, sender=Planner)
def update_trip_dates(sender, instance, created, **kwargs):
    # Getting all planners of the trip to figure out "Start Date" & "End Date"
    trip = instance.trip
    planners = trip.planners.all()
    print('All Planners are : ', planners)
    for planner in planners.order_by('start_date'):
        print(planner.created_at, planner.start_date)
    for planner in planners.order_by('end_date'):
        print(planner.created_at, planner.end_date)
    trip.start_date = planners.order_by('start_date').first().start_date
    trip.end_date = planners.order_by('end_date').last().end_date

    trip.save()