from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from models import Borrower

@receiver(post_save, sender=User)
def create_borrower_for_user(sender, instance, created, **kwargs):
    if created:
        Borrower.objects.create(
            user=instance,
            name=instance.username,   # REQUIRED
            phone="",                 # TEMP DEFAULT
            address=""                # TEMP DEFAULT
        )
