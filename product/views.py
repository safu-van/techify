from django.shortcuts import render,  redirect

from product.models import Product, ProductDetails
from category.models import Category

# Create your views here.

def product_list(request):
    products = Product.objects.exclude(is_available=False)
    return render(request, 'user/product_list.html', {'products': products})


def product_view(request, product_id):
    product = Product.objects.get(id=product_id)
    if product.is_available == True:
        product_details = ProductDetails.objects.get(product=product)
        category = product.category
        related_products = Product.objects.exclude(id=product_id).filter(category=category)
        context = {
            'product': product,
            'product_details': product_details,
            'related_products': related_products,
        }
        return render(request, 'user/product.html', context)
    return redirect('home:home_page')


def category_product(request, category_id):
    products = Product.objects.filter(category=category_id).exclude(is_available=False)
    return render(request, 'user/product_list.html', {'products': products})


def add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('product_name')
        category_name = request.POST.get('category')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        description = request.POST.get('description')
        additional_info = request.POST.get('additional_information')
        thumbnail = request.FILES.get('thumbnail')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        
        category = Category.objects.get(name=category_name)
        
        product = Product.objects.create(name=name, price=price, stock=stock, category=category, thumbnail=thumbnail, image2=image2, image3=image3)
        product.save()
        
        product_details = ProductDetails.objects.create(product=product, description=description, additional_information=additional_info)
        product_details.save()
        
        return redirect('admin_techify:product_management')
    return render(request, 'admin/add_product.html', {'categories':categories})


def product_action(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if product.is_available:
        product.is_available = False
    else:
        product.is_available = True
        
    product.save()
    return redirect('admin_techify:product_management')


def delete_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    return redirect('admin_techify:product_management')


def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    product_details = product.product_details
    
    if request.method == 'POST':
        name = request.POST.get('product_name')
        category_name = request.POST.get('category')
        stock = request.POST.get('stock')
        price = request.POST.get('price')
        description = request.POST.get('description')
        additional_info = request.POST.get('additional_information')
        thumbnail = request.FILES.get('thumbnail')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        
        product.name = name
        product.stock = stock
        product.price = price
        
        category = Category.objects.get(name=category_name)
        product.category = category
        
        product_details.description = description
        product_details.additional_information = additional_info
        product_details.save()
        
        if thumbnail:
            product.thumbnail = thumbnail
        if image2:
            product.image2 = image2
        if image3:
            product.image3 = image3
        
        product.save()  
        
        return redirect('admin_techify:product_management')
        
    context = {
        'product': product,
        'categories': categories,
        'product_details': product_details,
    }      
    return render(request, 'admin/edit_product.html', context)
    