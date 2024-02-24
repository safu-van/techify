from django.urls import path
from category import views

app_name = 'category'

urlpatterns = [
    path('category_action/<int:id>/', views.category_action, name="category_action")
]