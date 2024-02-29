from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from authentication.models import User


# Sign Up
def signup(request):
    if request.user.is_authenticated:
        return redirect('home:home_page')
    
    if request.method == 'POST':
        name = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            email_taken = True
            return render(request, 'authentication/signup.html', {'email_taken': email_taken})

        create_user = User.objects.create_user(full_name=name, email=email, password=password)
        create_user.save()
    return render(request, 'authentication/signup.html')


# Sign In
def signin(request):
    if request.user.is_authenticated:
        return redirect('home:home_page')
    
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            get_user = User.objects.filter(email=email).get()
        except User.DoesNotExist:
            pass

        user = authenticate(request, email=email, password=password)
        
        if user is not None and get_user.is_superuser:
            login(request, user)
            return redirect('admin_techify:admin_dashboard')
        elif user is not None and get_user.is_active:
            login(request, user)
            return redirect('home:home_page')
        else:
            user_isnotvalid = True
            return render(request, 'authentication/signin.html', {'user_isnotvalid': user_isnotvalid})
        
    return render(request, 'authentication/signin.html')


# Sign Out
def signout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home:home_page')


# User Block/Unblock
def user_action(request, user_id):
    user = User.objects.get(id=user_id)
    
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
         
    user.save()  
     
    return redirect('admin_techify:user_management')


# def otp(request):
#     if request.method == 'POST':
#         otp1 = request.POST.get("otp1")
#         otp2 = request.POST.get("otp2")
#         otp3 = request.POST.get("otp3")
#         otp4 = request.POST.get("otp4")

#         otp_code = otp1 + otp2 + otp3 + otp4
#         print(otp_code)
#     return render(request, 'authentication/otp.html')
