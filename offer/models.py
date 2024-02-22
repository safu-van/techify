from django.db import models

# Create your models here.

class Offer(models.Model):
    name = models.CharField(max_length=100)
    offer_percentage = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name