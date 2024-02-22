from django.urls import path
from product import views

app_name = 'product'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product_view/<int:id>/', views.product_view, name='product_view'),
    path('category_product/<int:id>/', views.category_product, name='category_product')
]