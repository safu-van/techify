from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from category.models import Category
from authentication.models import User
from product.models import Product

# Create your views here.

@login_required(login_url = 'authentication:signin')
def admin_home(request):
    if request.user.is_superuser:
        return render(request, 'admin/index.html')
    return redirect('authentication:signin')


@login_required(login_url = 'authentication:signin')
def users(request):
    user = User.objects.exclude(is_superuser=True)
    return render(request, 'admin/user.html', {'user': user})


@login_required(login_url = 'authentication:signin')
def category(request):
    categories = Category.objects.all()
    
    return render(request, 'admin/category.html', {'categories': categories})


@login_required(login_url = 'authentication:signin')
def add_category(request):
    if request.method == "POST":
        name = request.POST.get('category_name')
        image = request.FILES.get('category_image')
        
        add_category = Category.objects.create(name=name, image=image)
        add_category.save()
        
        return redirect('admin_techify:category')
    return render(request, 'admin/category.html')



@login_required(login_url = 'authentication:signin')
def edit_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == "POST":
        name = request.POST.get('category_name')
        image = request.FILES.get('category_image')
        
        category.name = name
        if image:
            category.image = image
        category.save()
        
        return redirect('admin_techify:category')
    return render(request, 'admin/edit_category.html', {'category':category})


@login_required(login_url = 'authentication:signin')
def product(request):
    category = Category.objects.all()
    product = Product.objects.all()
    
    context = {
        'category': category,
        'product': product,
    }
    return render(request, 'admin/product.html', context)
