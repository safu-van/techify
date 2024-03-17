from django.db import models


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images/category")
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

