from django.urls import path

from category import views

app_name = "category"

urlpatterns = [
    path(
        "category-action/<int:category_id>/",
        views.category_action,
        name="category_action",
    ),
    path("add-category/", views.add_category, name="add_category"),
    path("edit-category/<int:category_id>/", views.edit_category, name="edit_category"),
]
