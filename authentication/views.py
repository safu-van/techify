import random
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone

from authentication.models import User


# Send otp to mail
def send_otp(request):
    otp = random.randint(1000, 9999)
    request.session["generated_otp"] = otp
    otp_expiry_time = timezone.now() + timedelta(minutes=5)
    request.session["otp_expiry_time"] = otp_expiry_time.isoformat()

    request.session["message"] = "otp has sent to your email"

    user_name = request.session.get("name", "Sir/Mam")
    subject = "Techify Ecommerce"
    message = f"Hi {user_name},\n\n{otp} is your OTP for email verification.\nOTP is valid for 5 min"
    recipient = request.session.get("email")
    send_mail(
        subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=True
    )


# Resend otp
def resend_otp(request):
    request.session.pop("generated_otp", None)
    send_otp(request)
    return redirect("authentication:verify_email")


# Verify email using otp and save user
def verify_email(request):
    email = request.session.get("email")
    password = request.session.get("password")
    name = request.session.get("name")
    otp_expiry_time = request.session.get("otp_expiry_time")
    otp_expiry_time = timezone.datetime.fromisoformat(otp_expiry_time)

    # otp sended success message
    if "message" in request.session:
        message = request.session.pop("message")
    else:
        message = None

    if request.method == "POST":
        if timezone.now() > otp_expiry_time:
            request.session.pop("generated_otp", None)

        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")
        otp_code = otp1 + otp2 + otp3 + otp4

        generated_otp = request.session.get("generated_otp")
        if generated_otp is None:
            generated_otp = 00000

        if int(generated_otp) == int(otp_code):
            request.session.pop("generated_otp", None)
            if "forget_password" in request.session:
                request.session.pop("forget_password", None)
                return redirect("authentication:change_password")
            else:
                User.objects.create_user(email=email, password=password, name=name)
                user = authenticate(request, email=email, password=password)
                login(request, user)
                request.session.pop("password", None)
                request.session.pop("email", None)
                request.session.pop("name", None)
                request.session["message"] = "signed in successfully"
                return redirect("home:home_page")
        else:
            messages.error(request, "Invalid OTP Please try again")
    context = {"email": email, "message": message}
    return render(request, "authentication/otp.html", context)


# Sign Up
def signup(request):
    if request.user.is_authenticated:
        return redirect("home:home_page")

    if request.method == "POST":
        name = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            email_taken = True
            return render(
                request, "authentication/signup.html", {"email_taken": email_taken}
            )

        request.session["name"] = name
        request.session["email"] = email
        request.session["password"] = password

        send_otp(request)
        return redirect("authentication:verify_email")
    return render(request, "authentication/signup.html")


# Sign In
def signin(request):
    if request.user.is_authenticated:
        return redirect("home:home_page")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            get_user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user_isnotvalid = True
            return render(
                request,
                "authentication/signin.html",
                {"user_isnotvalid": user_isnotvalid},
            )

        user = authenticate(request, email=email, password=password)

        if user is not None and get_user.is_superuser:
            login(request, user)
            return redirect("admin_techify:admin_dashboard")
        elif user is not None and get_user.is_active:
            login(request, user)
            request.session["message"] = "Signed In Successfully"
            return redirect("home:home_page")
        else:
            user_isnotvalid = True
            return render(
                request,
                "authentication/signin.html",
                {"user_isnotvalid": user_isnotvalid},
            )
    return render(request, "authentication/signin.html")


# Sign Out
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("home:home_page")


# User Block/Unblock
def user_action(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
    except ObjectDoesNotExist:
        return redirect("admin_techify:user_management")
    return redirect("admin_techify:user_management")


# Forget Password (taking Email address from user and send otp)
def forget_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            request.session["email"] = email
            request.session["forget_password"] = "forget_password"
            send_otp(request)
            return redirect("authentication:verify_email")
        else:
            messages.error(request, "Email doesn't exists")
    return render(request, "authentication/password_assistance.html")


# Change Password (if the email is verified by otp)
def change_password(request):
    if "email" in request.session:
        email = request.session.get("email")
        if request.method == "POST":
            password = request.POST.get("password")
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                return redirect("authentication:signin")
            except ObjectDoesNotExist:
                return redirect("authentication:forget_password")
        return render(request, "authentication/change_password.html")
    return redirect("authentication:forget_password")
