from django.shortcuts import render

from category.models import Category
from product.models import Product


# Home Page
def home(request):
    categories = Category.objects.filter(is_available=True)
    products = Product.objects.filter(
        is_available=True, category__is_available=True, brand__is_available=True
    ).exclude(offer=None)

    # User signin  message
    if "message" in request.session:
        message = request.session.pop("message")
    else:
        message = None

    context = {
        "categories": categories,
        "products": products,
        "message": message,
    }
    return render(request, "user/index.html", context)
