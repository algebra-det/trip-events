from django.contrib import admin

from .models import NearestHotSpots, PlannerWishlist, Stay, Facility, StayImage, Booking, Review

class StayImageInline(admin.TabularInline):
    model = StayImage
    extra = 3
    
class NearestHotSpotsInline(admin.TabularInline):
    model = NearestHotSpots
    extra = 3
    

class StayAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'location', 'status')
    list_editable = ('status',)
    inlines = (StayImageInline, NearestHotSpotsInline)

admin.site.register(Stay, StayAdmin)

admin.site.register(Facility)
admin.site.register(Review)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'stay', 'price_of_stay', 'paid_amount', 'status')
    list_editable = ('status',)

admin.site.register(Booking, BookingAdmin)
admin.site.register(PlannerWishlist)