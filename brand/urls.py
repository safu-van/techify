from django.urls import path

from brand import views

app_name = "brand"

urlpatterns = [
    path("add-brand/", views.add_brand, name="add_brand"),
    path("edit-brand/<int:brand_id>/", views.edit_brand, name="edit_brand"),
    path("brand-action/<int:brand_id>/", views.brand_action, name="brand_action"),
]
