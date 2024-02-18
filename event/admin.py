from django.contrib import admin

from .models import Event, EventImage, Booking, PlannerWishlist, Review


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 3
    

class EventAdmin(admin.ModelAdmin):
    inlines = (EventImageInline,)


admin.site.register(Event, EventAdmin)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(PlannerWishlist)