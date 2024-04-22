from django.db import models

from product.models import Product
from authentication.models import User


# Wishlist Data
class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
