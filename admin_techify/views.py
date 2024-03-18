from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count


from category.models import Category
from authentication.models import User
from product.models import Product
from account.models import Orders


# Admin Dashboard
@login_required(login_url="authentication:signin")
def admin_dashboard(request):
    if request.user.is_superuser:
        return render(request, "admin/index.html")
    return redirect("home:home_page")


# User Management
@login_required(login_url="authentication:signin")
def user_management(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True).order_by("id")
        return render(request, "admin/user.html", {"users": users})
    return redirect("home:home_page")


# Category Management
@login_required(login_url="authentication:signin")
def category_management(request):
    if request.user.is_superuser:
        categories = Category.objects.annotate(
            products_count=Count("product")
        ).order_by("id")
        return render(request, "admin/category.html", {"categories": categories})
    return redirect("home:home_page")


# Product Management
@login_required(login_url="authentication:signin")
def product_management(request):
    if request.user.is_superuser:
        products = Product.objects.all().order_by("id")
        return render(request, "admin/product.html", {"products": products})
    return redirect("home:home_page")


# Order Management
@login_required(login_url="authentication:signin")
def order_management(request):
    if request.user.is_superuser:
        orders = Orders.objects.all().order_by("-id")
        return render(request, "admin/orders.html", {"orders": orders})
    return redirect("home:home_page")
