from django.urls import path
from coupon import views

app_name = "coupon"


urlpatterns = [
    path("add-coupon/", views.add_coupon, name="add_coupon"),
    path("edit-coupon/<int:coupon_id>/", views.edit_coupon, name="edit_coupon"),
    path("remove-coupon/<int:coupon_id>/", views.remove_coupon, name="remove_coupon"),
]
