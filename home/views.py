from django.shortcuts import render
from category.models import Category
from product.models import Product

# Create your views here.

def home(request):
    categories = Category.objects.exclude(is_available=False)
    products = Product.objects.exclude(is_available=False)
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'user/index.html', context)