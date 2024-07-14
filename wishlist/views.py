from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from product.models import Product
from authentication.models import User
from wishlist.models import Wishlist



# Wishlist
@login_required(login_url="authentication:signin")
def wishlist(request):
    user_id = request.user.id
    products = (
        Wishlist.objects.filter(user=user_id).select_related("product").order_by("-id")
    )
    
    return render(request, "user/wishlist.html", {"products": products})


# Add to Wishlist
@login_required(login_url="authentication:signin")
def add_to_wishlist(request):
    product_id = request.GET.get("id")
    user_id = request.user.id

    response_data = {}

    if Wishlist.objects.filter(product=product_id, user=user_id).exists():
        response_data["message"] = "Item already in wishlist"
    else:
        try:
            product = Product.objects.get(id=product_id)
            user = User.objects.get(id=user_id)
            new_item = Wishlist.objects.create(product=product, user=user)
            new_item.save()
            response_data["message"] = "Item added to wishlist"
        except ObjectDoesNotExist:
            response_data["message"] = "Item not found"

    return JsonResponse(response_data, status=200)


# Remove from Wishlist
@login_required(login_url="authentication:signin")
def remove_from_wishlist(request, product_id):
    response_data = {}
    try:
        product = Wishlist.objects.get(id=product_id)
        product.delete()
        response_data["message"] = "Item removed"
    except ObjectDoesNotExist:
        response_data["message"] = "Item not in wishlist"
    return JsonResponse(response_data, status=200)
