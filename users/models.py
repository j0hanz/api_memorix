from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Model for user profiles."""

    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', db_index=True
    )
    profile_picture = CloudinaryField(
        'image', default='nobody_nrbk5n', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username}'s profile"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for every new user."""
    if created or not hasattr(instance, 'profile'):
        Profile.objects.create(owner=instance)
    else:
        instance.profile.save()
