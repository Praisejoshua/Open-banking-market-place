"""
Signals for the accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserPreference


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create user preferences when a new user is created."""
    if created:
        UserPreference.objects.get_or_create(user=instance)
