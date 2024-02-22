from django.shortcuts import render

# Create your views here.

def signup(request):
    if request.method == 'POST':
        name = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(name, email, password)
    return render(request, 'authentication/signup.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(email, password)
    return render(request, 'authentication/signin.html')