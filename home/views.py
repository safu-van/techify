from django.shortcuts import render

from category.models import Category
from product.models import Product


# Home Page
def home(request):
    categories = Category.objects.exclude(is_available=False)
    products = Product.objects.filter(is_available=True).exclude(category__is_available=False)
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'user/index.html', context)