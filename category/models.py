import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/category')
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
# Delete the category image from the media folder when the category is deleted
@receiver(pre_delete, sender=Category)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)