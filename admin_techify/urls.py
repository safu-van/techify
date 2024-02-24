from django.urls import path
from admin_techify import views

app_name = 'admin_techify'

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('category/', views.category, name='category'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('user/', views.users, name='users'),
    path('product/', views.product, name='product'),
]