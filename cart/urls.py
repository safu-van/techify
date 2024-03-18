from django.urls import path
from cart import views

app_name = "cart"

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path(
        "remove-from-cart/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("update_quantity/", views.update_quantity, name="update_quantity"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/", views.order_success, name="order_success"),
]
