from django.urls import path

from product import views

app_name = "product"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("filtered-product", views.filtered_products, name="filtered_products"),
    path("search/", views.search_products, name="search_product"),
    path("product-view/<int:product_id>/", views.product_view, name="product_view"),
    path(
        "category-product/<int:category_id>/",
        views.category_product,
        name="category_product",
    ),
    path("add-product/", views.add_product, name="add_product"),
    path(
        "product-action/<int:product_id>/", views.product_action, name="product_action"
    ),
    path("edit-product/<int:product_id>/", views.edit_product, name="edit_product"),
]
