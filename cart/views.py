from django.shortcuts import render
from django.http import JsonResponse

from cart.models import CartItems
from product.models import Product
from authentication.models import User


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


def add_to_cart(request):
    product_id = request.GET.get("id")
    quantity = request.GET.get("qty")
    user_id = request.user.id

    product = Product.objects.get(id=product_id)
    stock_of_product = product.stock

    if CartItems.objects.filter(product_id=product_id, user_id=user_id).exists():
        item = CartItems.objects.get(product_id=product_id, user_id=user_id)
        if item.quantity < stock_of_product:
            item.quantity += 1
            item.save()
    else:
        if stock_of_product > 0:
            user = User.objects.get(id=user_id)
            new_item = CartItems.objects.create(
                product_id=product, quantity=quantity, user_id=user
            )
            new_item.save()
    return JsonResponse(data={}, status=204, safe=False)


def remove_from_cart(request, item_id):
    item = CartItems.objects.get(id=item_id)
    item.delete()
    return JsonResponse(data={}, status=204, safe=False)


def update_quantity(request):
    item_id = request.GET.get("id")
    quantity = request.GET.get("qty")
    item = CartItems.objects.get(id=item_id)
    item.quantity = int(quantity)
    item.save()

    return JsonResponse(data={}, status=204, safe=False)
