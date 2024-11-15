from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefono']
    search_fields = ['user__username', 'telefono']

# Extender el UserAdmin existente
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
