from django.contrib import admin

from .models import Booking, LogComment, LogFiles, MemberUser, PlannerComment, PlannerLikes, Request, Trip, ExpenseType, Expense, Log, Planner, TripComment, TripLikes, TripVideos

admin.site.register(Trip)
admin.site.register(TripVideos)
admin.site.register(TripLikes)
admin.site.register(TripComment)
admin.site.register(MemberUser)
admin.site.register(Booking)
admin.site.register(Planner)
admin.site.register(PlannerLikes)
admin.site.register(PlannerComment)
admin.site.register(ExpenseType)
admin.site.register(Expense)
admin.site.register(Log)
admin.site.register(LogFiles)
admin.site.register(LogComment)
admin.site.register(Request)