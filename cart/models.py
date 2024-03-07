from django.db import models

from product.models import Product
from authentication.models import User


class CartItems(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    