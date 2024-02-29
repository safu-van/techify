import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from category.models import Category
from offer.models import Offer



# Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.IntegerField()
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='images/product')
    image2 = models.ImageField(upload_to='images/product')
    image3 = models.ImageField(upload_to='images/product')

    def __str__(self) -> str:
        return self.name


# Delete product image from media folder when product deleted
@receiver(pre_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
    if instance.image2:
        if os.path.isfile(instance.image2.path):
            os.remove(instance.image2.path)
    if instance.image3:
        if os.path.isfile(instance.image3.path):
            os.remove(instance.image3.path)
    

# Product Details Model
class ProductDetails(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='product_details')
    description = models.TextField()
    additional_information = models.TextField()

    def __str__(self) -> str:
        return self.product.name + " " + 'Details'