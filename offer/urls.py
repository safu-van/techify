from django.urls import path

from offer import views

app_name = "offer"

urlpatterns = [
    path("add-offer/", views.add_offer, name="add_offer"),
    path("edit-offer/<int:offer_id>/", views.edit_offer, name="edit_offer"),
    path("remove-offer/<int:offer_id>/", views.remove_offer, name="remove_offer"),
]
