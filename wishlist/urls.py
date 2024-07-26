from django.urls import path
from wishlist import views

app_name = "wishlist"


urlpatterns = [
    path("", views.wishlist, name="wishlist"),
    path("add-to-wishlist", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "remove-from-wishlist/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
]
