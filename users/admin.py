from django.contrib import admin
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import UserProfile
from django.contrib.auth.models import User

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefono']
    search_fields = ['user__username', 'telefono']

# Create UserProfiles after migrations are complete
@receiver(post_migrate)
def create_user_profiles(sender, **kwargs):
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)
