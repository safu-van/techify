from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from category.models import Category
from authentication.models import User
from product.models import Product

# Create your views here.


@login_required(login_url = 'authentication:signin')
def admin_dashboard(request):
    if request.user.is_superuser:
        return render(request, 'admin/index.html')
    return redirect('home:home_page')


@login_required(login_url = 'authentication:signin')
def user_management(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True).order_by('id')
        return render(request, 'admin/user.html', {'users': users})
    return redirect('home:home_page')


@login_required(login_url = 'authentication:signin')
def category_management(request):
    if request.user.is_superuser:
        categories = Category.objects.all().order_by('id')
        return render(request, 'admin/category.html', {'categories': categories})
    return redirect('home:home_page')


@login_required(login_url = 'authentication:signin')
def product_management(request):
    if request.user.is_superuser:
        categories = Category.objects.all()
        products = Product.objects.all()
        context = {
            'categories': categories,
            'products': products,
        }
        return render(request, 'admin/product.html', context)
    return redirect('home:home_page')
