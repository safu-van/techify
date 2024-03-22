from django.db import models

from product.models import Product
from authentication.models import User
from account.models import UserAddress


# Cart 
class CartItems(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()


# Orders
class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_date = models.DateField()
    total = models.IntegerField()
    status = models.CharField(max_length=100)
    delivered_date = models.DateField(null=True)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)