# ticketing/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for new users."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created, if it doesn't exist.
    """
    logger.info(f"Signal triggered for user: {instance.username}, created={created}")
    if created:
        try:
            if not hasattr(instance, 'userprofile'):
                UserProfile.objects.create(user=instance)
                logger.info(f"Created UserProfile for user: {instance.username}")
            else:
                logger.info(f"UserProfile already exists for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error in save_user_profile signal: {e}")
            raise