from django.urls import path
from account import views

app_name = "account"


urlpatterns = [
    path("", views.account_settings, name="account_settings"),

    path("referral-code", views.generate_referral_code, name="get_referral_code"),

    path("orders/", views.orders, name="orders"),
    path("order-details/<int:order_id>/", views.order_details, name="order_details"),
    path(
        "download-invoice/<int:order_id>/",
        views.download_product_invoice,
        name="download_invoice",
    ),

    path("address/", views.address, name="address"),
    path("add-address/", views.add_address, name="add_address"),
    path(
        "remove-address/<int:address_id>/", views.remove_address, name="remove_address"
    ),
    path("edit-address/<int:address_id>/", views.edit_address, name="edit_address"),

    path("wallet/", views.wallet, name="wallet"),

    path("change-password/", views.change_password, name="change_password"),
]
