from django.urls import path
from authentication import views

app_name = "authentication"


urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("user-action/<int:user_id>/", views.user_action, name="user_action"),
    path("verify-email/", views.verify_email, name="verify_email"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("forget-password/", views.forget_password, name="forget_password"),
    path("change-password/", views.change_password, name="change_password"),
]
