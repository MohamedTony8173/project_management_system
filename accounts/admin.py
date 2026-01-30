from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Profile

class UserCustomAdmin(UserAdmin):
    list_display = ['email','username','is_active','is_staff','is_superuser']
    
    fieldsets = (
        (None, {
            "fields": (
                'password','email','username'
            ),
        }),
        ('Permissions', {
            "fields": (
                'is_active','is_staff','is_superuser'
            ),
        }),
        ('Authority', {
            "fields": (
                'groups','user_permissions'
            ),
        }),
    )
    
admin.site.register(User,UserCustomAdmin)
admin.site.register(Profile)