from django.contrib import admin
from django.contrib.auth.models import Group
from .models import MyUser, Code, TempToken
@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'email', 'name', 'is_verified', 'sign_up_steps')


@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'confirmation_code', 'usage')

admin.site.register(TempToken)
admin.site.unregister(Group)