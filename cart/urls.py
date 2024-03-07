from django.urls import path
from cart import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]