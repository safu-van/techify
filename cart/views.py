import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from cart.models import CartItems, Orders
from product.models import Product
from authentication.models import User
from account.models import UserAddress

from datetime import date



# Cart 
@login_required(login_url="authentication:signin")
def cart(request):
    user_id = request.user.id
    cart_items = CartItems.objects.filter(user_id=user_id).order_by("-id")
    cart_details = []

    for item in cart_items:
        product_name = item.product_id.name
        product_image = item.product_id.thumbnail.url
        product_price = item.product_id.price
        total_price = product_price * item.quantity
        item_id = item.id
        stock_of_product = item.product_id.stock
        cart_details.append(
            {
                "product_name": product_name,
                "product_image": product_image,
                "product_price": product_price,
                "quantity": item.quantity,
                "total_price": total_price,
                "item_id": item_id,
                "stock_of_product": stock_of_product,
            }
        )

    total = sum(item["total_price"] for item in cart_details)

    context = {
        "cart_details": cart_details,
        "total": total,
    }
    return render(request, "user/cart.html", context)


# Add Product to Cart
@login_required(login_url="authentication:signin")
def add_to_cart(request):
    product_id = request.GET.get("id")
    quantity = request.GET.get("qty")
    user_id = request.user.id

    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        pass

    stock_of_product = product.stock
    total = float(product.price) * int(quantity)

    if CartItems.objects.filter(product_id=product_id, user_id=user_id).exists():
        try:
            item = CartItems.objects.get(product_id=product_id, user_id=user_id)
        except ObjectDoesNotExist:
            pass
        check = item.quantity + int(quantity)
        if item.quantity < stock_of_product and check < stock_of_product:
            item.total = total
            item.quantity = quantity
            item.save()
    else:
        if stock_of_product > 0:
            try:
                user = User.objects.get(id=user_id)
            except ObjectDoesNotExist:
                pass
            new_item = CartItems.objects.create(
                product_id=product, quantity=quantity, user_id=user, total=total
            )
            new_item.save()
    return JsonResponse(data={}, status=204, safe=False)


# Remove from Cart
@login_required(login_url="authentication:signin")
def remove_from_cart(request, item_id):
    try:
        item = CartItems.objects.get(id=item_id)
        item.delete()
    except ObjectDoesNotExist:
        pass
    return JsonResponse(data={}, status=204, safe=False)

# Update Product quantity 
@csrf_exempt
def update_quantity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("productId")
            value = data.get("value")
            user = request.user.id

            item = CartItems.objects.get(id=product_id, user_id=user)
            item.total = item.product_id.price * value
            item.quantity = value
            item.save()
            return JsonResponse(
                {"message": "Quantity received successfully"}, status=200
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


# Checkout
@login_required(login_url="authentication:signin")
def checkout(request):
    user_id = request.user.id
    if request.method == "POST":
        address_id = request.POST.get("selectedAddressId")
        total_sum = request.POST.get("total_sum")
        status = "PENDING"
        ordered_date = date.today()
        ordered_products = CartItems.objects.filter(user_id=user_id)

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            pass

        try:
            delivery_address = UserAddress.objects.get(id=address_id)
        except ObjectDoesNotExist:
            pass

        for product in ordered_products:
            try:
                item = Product.objects.get(name=product.product_id)
                item.stock = item.stock - product.quantity
                item.save()
            except ObjectDoesNotExist:
                pass
            ordered_items = Orders.objects.create(
                user=user,
                ordered_date=ordered_date,
                total=total_sum,
                status=status,
                address=delivery_address,
                product=item,
            )
            ordered_items.save()

        CartItems.objects.filter(user_id=user_id).delete()

        return redirect("cart:order_success")
    
    addresses = UserAddress.objects.filter(user=user_id, status=True)
    products = CartItems.objects.filter(user_id=user_id).annotate(
        sub_total=Sum("total")
    )
    sub_total = products.aggregate(sub_total=Sum("total"))["sub_total"]
    shipping = "Free shipping"
    if sub_total < 50:
        shipping = 20
    if shipping == 20:
        total = sub_total + 20
    else:
        total = sub_total
    context = {
        "addresses": addresses,
        "products": products,
        "sub_total": sub_total,
        "shipping": shipping,
        "total": total,
    }
    return render(request, "user/checkout.html", context)


# Order Success Page
@login_required(login_url="authentication:signin")
def order_success(request):
    return render(request, "user/order_success.html")
