from django.db import models

from product.models import Product
from authentication.models import User


# Cart Data
class CartItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=30, decimal_places=1)


# Delivery Address
class DeliveyAddress(models.Model):
    name = models.CharField(max_length=100)
    phone = models.BigIntegerField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, null=True)


# Order Data
class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_date = models.DateField()
    delivered_date = models.DateField(null=True)
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="Pending")
    address = models.ForeignKey(DeliveyAddress, on_delete=models.CASCADE)
    sub_total = models.DecimalField(max_digits=30, decimal_places=1)
    discount_amt = models.DecimalField(max_digits=30, decimal_places=1, default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=30, decimal_places=1)
    product_qty = models.PositiveIntegerField()

    @property
    def total(self):
        return self.sub_total - self.discount_amt
