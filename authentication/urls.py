from django.urls import path
from authentication import views

app_name = 'authentication'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('user_action/<int:id>/', views.user_action, name='user_action'),
    path('otp/', views.otp, name='otp'),
]