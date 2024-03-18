import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from cart.models import CartItems
from product.models import Product
from authentication.models import User
from account.models import UserAddress, Orders

from datetime import date



def cart(request):
    if request.user.is_authenticated:
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
    return redirect('home:home_page')

def add_to_cart(request):
    if request.user.is_authenticated:
        product_id = request.GET.get("id")
        quantity = request.GET.get("qty")
        user_id = request.user.id
        
        product = Product.objects.get(id=product_id)
        stock_of_product = product.stock
        total = float(product.price) * int(quantity)


        if CartItems.objects.filter(product_id=product_id, user_id=user_id).exists():
            item = CartItems.objects.get(product_id=product_id, user_id=user_id)
            check = item.quantity + int(quantity)
            if item.quantity < stock_of_product and check < stock_of_product :
                item.total = total
                item.quantity = quantity
                item.save()
        else:
            if stock_of_product > 0:
                user = User.objects.get(id=user_id)
                new_item = CartItems.objects.create(
                    product_id=product, quantity=quantity, user_id=user, total=total
                )
                new_item.save()
        return JsonResponse(data={}, status=204, safe=False)
    return redirect('home:home_page')


def remove_from_cart(request, item_id):
    item = CartItems.objects.get(id=item_id)
    item.delete()
    return JsonResponse(data={}, status=204, safe=False)


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


def checkout(request):
    user_id = request.user.id
    if request.method == "POST":
        address_id = request.POST.get('selectedAddressId')
        total_sum = request.POST.get('total_sum')
        status = "PENDING"
        ordered_date = date.today()
        ordered_products = CartItems.objects.filter(user_id=user_id)
        user = User.objects.get(id=user_id)
        delivery_address = UserAddress.objects.get(id=address_id)

        for product in ordered_products:
            item = Product.objects.get(name=product.product_id)
            item.stock = item.stock - product.quantity
            item.save()
            ordered_items = Orders.objects.create(
                user=user, ordered_date=ordered_date, total=total_sum, status=status, address=delivery_address, product=item
            )
            ordered_items.save()

        CartItems.objects.filter(user_id=user_id).delete()

        
        return redirect('cart:order_success')
    addresses = UserAddress.objects.filter(user=user_id, status=True)
    products = CartItems.objects.filter(user_id=user_id).annotate(sub_total=Sum('total'))
    sub_total = products.aggregate(sub_total=Sum('total'))['sub_total']
    shipping = 'Free shipping'
    if sub_total < 50:
        shipping = 20
    if shipping == 20:
        total = sub_total + 20
    else:
        total = sub_total    
    context = {
        'addresses': addresses,
        'products': products,
        'sub_total': sub_total,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'user/checkout.html', context)

def order_success(request):
    return render(request, 'user/order_success.html')