import os
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.db.models import Avg
from django.db.models.signals import pre_save
from django.dispatch import receiver

from category.models import Category
from brand.models import Brand
from offer.models import Offer
from authentication.models import User


# Product
class Product(models.Model):
    name = models.CharField(max_length=200)
    p_price = models.DecimalField(max_digits=30, decimal_places=1)
    stock = models.IntegerField()
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to="images/product")
    image2 = models.ImageField(upload_to="images/product")
    image3 = models.ImageField(upload_to="images/product")

    @property
    def price(self):
        if self.offer:
            discounted_amount = self.p_price * (
                Decimal(self.offer.discount) / Decimal(100)
            )
            offer_price = (self.p_price - discounted_amount).quantize(
                Decimal("0.0"), rounding=ROUND_HALF_UP
            )
            return offer_price
        else:
            return self.p_price

    @property
    def average_rating(self):
        avg_rating = self.reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        avg_rating_percentage = (avg_rating / 5) * 100
        return avg_rating_percentage


# To delete old product images before saving new images
@receiver(pre_save, sender=Product)
def delete_old_images(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        else:
            image_fields = ["thumbnail", "image2", "image3"]
            for field_name in image_fields:
                old_image_field = getattr(old_instance, field_name)
                new_image_field = getattr(instance, field_name)
                if old_image_field != new_image_field:
                    old_image_path = old_image_field.path
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)


# Product Details
class ProductDetails(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="product_details"
    )
    description = models.TextField()
    additional_information = models.TextField()


# Product Rating & Review
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(default=0)

    @property
    def rating_percentage(self):
        return (self.rating / 5) * 100
