from django.db import models

from authentication.models import User


# Coupon
class Coupon(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=150)
    discount_percentage = models.IntegerField()
    limit = models.IntegerField()
    expiry_date = models.DateField()


# Coupon Usage Data
class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
