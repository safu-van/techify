from django.urls import path
from offer import views

app_name = "offer"


urlpatterns = [
    path("add-offer/", views.add_offer, name="add_offer"),
    path("edit-offer/<int:offer_id>/", views.edit_offer, name="edit_offer"),
    path("remove-offer/<int:offer_id>/", views.remove_offer, name="remove_offer"),
    path(
        "product-offer/<int:product_id>/<int:offer_id>/",
        views.product_offer,
        name="product_offer",
    ),
    path(
        "remove-product-offer/<int:product_id>/",
        views.remove_product_offer,
        name="remove_product_offer",
    ),
    path(
        "category-offer/<int:category_id>/<int:offer_id>/",
        views.category_offer,
        name="category_offer",
    ),
    path(
        "remove-category-offer/<int:category_id>/",
        views.remove_category_offer,
        name="remove_category_offer",
    ),
]
