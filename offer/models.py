from django.db import models
from django.utils import timezone


# Offer
class Offer(models.Model):
    name = models.CharField(max_length=100)
    discount = models.IntegerField()
    active_date = models.DateField()
    expiry_date = models.DateField()

    def is_active(self):
        today = timezone.now().date()
        return self.active_date <= today <= self.expiry_date
