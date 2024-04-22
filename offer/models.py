from django.db import models


# Offer
class Offer(models.Model):
    name = models.CharField(max_length=100)
    discount = models.IntegerField()
    active_date = models.DateField()
    expiry_date = models.DateField()
