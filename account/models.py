from django.db import models

from authentication.models import User
from product.models import Product


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.BigIntegerField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255)
    status = models.BooleanField(default=True)



class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_date = models.DateField()
    total = models.IntegerField()
    status = models.CharField(max_length=100)
    deliverd_date = models.DateField(null=True)
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

