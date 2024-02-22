from django.shortcuts import render
from product.models import Product, ProductDetails

# Create your views here.

def product_list(request):
    products = Product.objects.all()
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
    products = Product.objects.filter(category=id)
    context = {
        'products': products,
    }
    return render(request, 'user/product_list.html', context)