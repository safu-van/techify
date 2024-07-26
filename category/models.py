import os

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from offer.models import Offer


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="images/category")
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True)
    is_available = models.BooleanField(default=True)


# To delete old category images before saving new images
@receiver(pre_save, sender=Category)
def delete_old_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        else:
            if old_instance.image != instance.image:
                old_image_path = old_instance.image.path
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)
