from django.db import models


# Brand
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_available = models.BooleanField(default=True)
