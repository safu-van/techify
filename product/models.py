import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from category.models import Category
from offer.models import Offer

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    thumbnail = models.ImageField(upload_to='images/product')
    stock = models.IntegerField()
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


# Delete the product image from the media folder when the product is deleted
@receiver(pre_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
    

class ProductDetails(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    description = models.TextField()
    additional_information = models.TextField()

    def __str__(self) -> str:
        return self.product.name + " " + 'Details'