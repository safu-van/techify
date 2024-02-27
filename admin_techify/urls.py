from django.urls import path

from admin_techify import views

app_name = 'admin_techify'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('category-management/', views.category_management, name='category_management'),
    path('user-management/', views.user_management, name='user_management'),
    path('product-management/', views.product_management, name='product_management'),
]