import random

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

from authentication.models import User


# Send otp to mail
def send_otp(request):
    otp = random.randint(1000, 9999)
    request.session["generated_otp"] = otp
    otp_expiry_time = timezone.now() + timedelta(minutes=5)
    request.session['otp_expiry_time'] = otp_expiry_time.isoformat()

    request.session['message'] = 'otp has sent to your email'

    user_name = request.session.get("name")
    subject = "Techify Ecommerce"
    message = f"Welcome {user_name},\n\n{otp} is your OTP for email verification.\nOTP is valid for 5 min"
    recipient = request.session.get("email")
    send_mail(
        subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False
    )   


# Resend otp
def resend_otp(request):
    del request.session["generated_otp"]
    send_otp(request)
    return redirect("authentication:verify_email")


# Verify email and save user
def verify_email(request):
    email = request.session.get("email")
    password = request.session.get("password")
    name = request.session.get("name")
    otp_expiry_time = request.session.get("otp_expiry_time")
    otp_expiry_time = timezone.datetime.fromisoformat(otp_expiry_time)

    if 'message' in request.session:
        message = request.session.pop('message')
    else:
        message = None

    if request.method == "POST":
        if timezone.now() > otp_expiry_time and 'generated_otp' in request.session:
            del request.session["generated_otp"]

        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")
        otp_code = otp1 + otp2 + otp3 + otp4
        
        generated_otp = request.session.get("generated_otp")
        if generated_otp is None:
            generated_otp = 12345
        
        if int(generated_otp) == int(otp_code):
            del request.session["generated_otp"]
            User.objects.create_user(email=email, password=password, name=name)
            user = authenticate(request, email=email, password=password)
            login(request, user)
            request.session['message'] = 'signed in successfully'
                
            return redirect("home:home_page")
        else:
            messages.error(request, "Invalid OTP Please try again")
    context = {
        "email": email,
        "message": message
    }
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
            pass

        user = authenticate(request, email=email, password=password)

        if user is not None and get_user.is_superuser:
            login(request, user)
            return redirect("admin_techify:admin_dashboard")
        elif user is not None and get_user.is_active:
            login(request, user)
            request.session['message'] = 'Signed In Successfully'
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
        pass

    return redirect("admin_techify:user_management")
