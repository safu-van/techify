from django.urls import path
from account import views

app_name = "account"

urlpatterns = [
    path("", views.account_settings, name="account_settings"),
    path("orders/", views.orders, name="orders"),
    path(
        "order-status/<int:order_id>/<str:status>/",
        views.order_status,
        name="order_status",
    ),
    path("address/", views.address, name="address"),
    path("add-address/", views.add_address, name="add_address"),
    path(
        "remove-address/<int:address_id>/", views.remove_address, name="remove_address"
    ),
    path("edit-address/<int:address_id>/", views.edit_address, name="edit_address"),
    path("change-password/", views.change_password, name="change_password"),
]
