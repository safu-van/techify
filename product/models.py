from django.db import models

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
    thumbnail = models.ImageField(upload_to="images/product")
    image2 = models.ImageField(upload_to="images/product")
    image3 = models.ImageField(upload_to="images/product")

    def __str__(self) -> str:
        return self.name


# Product Details Model
class ProductDetails(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="product_details"
    )
    description = models.TextField()
    additional_information = models.TextField()

    def __str__(self) -> str:
        return self.product.name + " " + "Details"
