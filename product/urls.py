from django.urls import path
from product import views

app_name = "product"


urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product-view/<int:product_id>/", views.product_view, name="product_view"),
    path("add-product/", views.add_product, name="add_product"),
    path("edit-product/<int:product_id>/", views.edit_product, name="edit_product"),
    path(
        "product-action/<int:product_id>/", views.product_action, name="product_action"
    ),
    path("add_review/", views.add_review, name="add_review"),
]
