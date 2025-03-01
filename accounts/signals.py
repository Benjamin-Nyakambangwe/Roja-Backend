from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LandlordProfile, LandlordBalance


@receiver(post_save, sender=LandlordProfile)
def create_landlord_balance(sender, instance, created, **kwargs):
    """Create a LandlordBalance when a LandlordProfile is created"""
    if created:
        LandlordBalance.objects.get_or_create(landlord=instance.user)
