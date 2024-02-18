from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stay

@receiver(post_save, sender=Stay)
def update_stay_mattress(sender, instance, created, **kwargs):
    post_save.disconnect(update_stay_mattress, sender=sender)
    if not instance.extra_mattress_available:
        instance.price_per_extra_mattress = None
        instance.number_of_extra_mattress_available = None
        instance.save()
    post_save.connect(update_stay_mattress, sender=sender)
post_save.connect(update_stay_mattress, sender= Stay)