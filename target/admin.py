from django.contrib import admin

from .models import TargetTrip, Expense, Log, Planner, Booking

admin.site.register(TargetTrip)
admin.site.register(Expense)
admin.site.register(Log)
admin.site.register(Planner)
admin.site.register(Booking)