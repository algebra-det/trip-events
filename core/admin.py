from django.contrib import admin

from .models import BlueTickRequest, Profile, BankDetails

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(BankDetails)
admin.site.register(BlueTickRequest)
