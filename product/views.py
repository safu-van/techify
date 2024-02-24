from django.shortcuts import render,  redirect
from product.models import Product, ProductDetails
from category.models import Category

# Create your views here.

def product_list(request):
    products = Product.objects.exclude(is_available=False)
    context = {
        'products': products,
    }
    return render(request, 'user/product_list.html', context)


def product_view(request, id):
    product = Product.objects.get(id=id)
    product_details = ProductDetails.objects.get(product=product)
    category = product.category
    related_products = Product.objects.exclude(id=id).filter(category=category)
    context = {
        'product': product,
        'product_details': product_details,
        'related_products': related_products,
    }
    return render(request, 'user/product.html', context)

def category_product(request, id):
    products = Product.objects.filter(category=id).exclude(is_available=False)
    context = {
        'products': products,
    }
    return render(request, 'user/product_list.html', context)

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_name = request.POST.get('selected_option')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        description = request.POST.get('description')
        additional_info = request.POST.get('additional_info')
        thumbnail = request.FILES.get('thumbnail_image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        
        category = Category.objects.get(id=category_name)
        
        product = Product.objects.create(name=name, price=price, stock=stock, category=category, thumbnail=thumbnail, image2=image2, image3=image3)
        product.save()
        product_details = ProductDetails.objects.create(product=product ,description=description, additional_information=additional_info)
        product_details.save()
        
        return redirect('admin_techify:product')
    return render(request, 'admin/product.html')

def product_action(request, id):
    product = Product.objects.get(id=id)
    if product.is_available:
        product.is_available = False
    else:
        product.is_available = True
        
    product.save()
    return redirect('admin_techify:product')