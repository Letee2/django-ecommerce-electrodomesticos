from django.contrib import admin
from .models import UserProfile
from django.contrib.auth.models import User

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefono']
    search_fields = ['user__username', 'telefono']
