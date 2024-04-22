import os

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from category.models import Category
from offer.models import Offer


# Product
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.IntegerField()
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to="images/product")
    image2 = models.ImageField(upload_to="images/product")
    image3 = models.ImageField(upload_to="images/product")


# Signal receiver function to delete old product images before saving new ones
@receiver(pre_save, sender=Product)
def delete_old_images(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        else:
            image_fields = ["thumbnail", "image2", "image3"]
            for field_name in image_fields:
                old_image_field = getattr(old_instance, field_name)
                new_image_field = getattr(instance, field_name)
                if old_image_field != new_image_field:
                    old_image_path = old_image_field.path
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)


# Product Details
class ProductDetails(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="product_details"
    )
    description = models.TextField()
    additional_information = models.TextField()
