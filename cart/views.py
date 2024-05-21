import json
from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from authentication.models import User
from account.models import UserAddress
from cart.models import CartItems, Orders, DeliveyAddress
from cart.utils import (
    update_wallet,
    update_product_stock,
    check_product_stock,
    withdraw_from_wallet,
)
from coupon.models import Coupon, CouponUsage
from product.models import Product


# Cart
@login_required(login_url="authentication:signin")
def cart(request):
    user_id = request.user.id
    cart_items = CartItems.objects.filter(user=user_id).order_by("-id")
    cart_details = []

    if "message" in request.session:
        message = request.session.pop("message")
    else:
        message = None

    for item in cart_items:
        product_name = item.product.name
        product_image = item.product.thumbnail.url
        product_price = item.product.price
        product_quantity = item.quantity
        total_price = item.total
        item_id = item.id
        stock_of_product = item.product.stock
        cart_details.append(
            {
                "product_name": product_name,
                "product_image": product_image,
                "product_price": product_price,
                "quantity": product_quantity,
                "total_price": total_price,
                "item_id": item_id,
                "stock_of_product": stock_of_product,
            }
        )

    total = sum(item["total_price"] for item in cart_details)

    context = {
        "cart_details": cart_details,
        "total": total,
        "message": message,
    }
    return render(request, "user/cart.html", context)


# Add Product to Cart
@login_required(login_url="authentication:signin")
def add_to_cart(request):
    product_id = request.GET.get("id")
    quantity = request.GET.get("qty")
    user_id = request.user.id

    response_data = {}

    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        response_data["message"] = "Product not found"

    stock_of_product = product.stock

    if CartItems.objects.filter(product=product_id, user=user_id).exists():
        response_data["message"] = "Item already in cart"
    else:
        if stock_of_product > 0 and int(quantity) <= stock_of_product:
            try:
                user = User.objects.get(id=user_id)
                new_item = CartItems.objects.create(
                    product=product, quantity=quantity, user=user
                )
                new_item.save()
                response_data["message"] = "Item added to cart"
            except ObjectDoesNotExist:
                return redirect("authentication:signin")
        else:
            response_data["message"] = "Insufficient stock"

    return JsonResponse(response_data, status=200)


# Remove from Cart
@login_required(login_url="authentication:signin")
def remove_from_cart(request, item_id):
    response_data = {}
    try:
        item = CartItems.objects.get(id=item_id)
        item.delete()
        response_data["message"] = "Item removed"
    except ObjectDoesNotExist:
        response_data["message"] = "Item not in the cart"
    return JsonResponse(response_data, status=200)


# Update Product quantity
@csrf_exempt
def update_quantity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get("productId")
            value = data.get("value")
            user = request.user.id

            item = CartItems.objects.get(id=product_id, user=user)
            item.quantity = value
            item.save()
            return JsonResponse(
                {"message": "Quantity received successfully"}, status=200
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


# Remove coupon from checkout
def remove_coupon(request):
    request.session.pop("discount_percentage", None)
    request.session.pop("coupon_code", None)
    request.session.pop("coupon_id", None)
    return redirect("cart:checkout")


# Checkout
@login_required(login_url="authentication:signin")
def checkout(request):
    try:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect("authentication:signin")

    if not check_product_stock(request):
        return redirect("cart:cart")

    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.limit == 0 or coupon.expiry_date < timezone.now().date():
                request.session["message"] = "Invalid Coupon"
            else:
                if CouponUsage.objects.filter(coupon=coupon, user=user).exists():
                    request.session["message"] = "Coupon Already Used"
                else:
                    request.session["discount_percentage"] = coupon.discount_percentage
                    request.session["coupon_code"] = coupon_code
                    request.session["coupon_id"] = coupon.id
            return redirect("cart:checkout")
        except ObjectDoesNotExist:
            request.session["message"] = "Invalid Coupon"
            request.session.pop("discount_percentage", None)
            request.session.pop("coupon_code", None)
            request.session.pop("coupon_id", None)

    # Message of Address (Added/Edited) or coupon or wallet
    if "message" in request.session:
        message = request.session.pop("message")
    else:
        message = False

    addresses = UserAddress.objects.filter(user=user_id)
    products = CartItems.objects.filter(user=user_id)
    sub_total = sum(item.total for item in products)
    total = sub_total

    if "discount_percentage" in request.session:
        discount_percentage = request.session.get("discount_percentage")
        discount_amt = sub_total * (Decimal(discount_percentage) / Decimal("100"))
        total = sub_total - discount_amt
    else:
        discount_amt = False

    # To access in place_order()
    request.session["total_amount"] = str(total)

    if "coupon_code" in request.session:
        coupon_code = request.session.get("coupon_code")
    else:
        coupon_code = False

    context = {
        "addresses": addresses,
        "message": message,
        "products": products,
        "sub_total": sub_total,
        "total": total,
        "discount_amt": discount_amt,
        "coupon_code": coupon_code,
    }
    return render(request, "user/checkout.html", context)


# Place Order
@login_required(login_url="authentication:signin")
@csrf_exempt
def place_order(request):
    if request.method == "POST":
        try:
            user_id = request.user.id
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return redirect("authentication:signin")

        if not check_product_stock(request):
            return redirect("cart:cart")

        address_id = request.POST.get("selectedAddressId")
        payment_method = request.POST.get("payment_method")
        ordered_date = date.today()
        ordered_products = CartItems.objects.filter(user=user)
        total_amount = request.session.pop("total_amount")

        if payment_method == "Cash on Delivery":
            if Decimal(total_amount) > 1000:
                request.session["message"] = (
                    "Cash on Delivery is not available for orders exceeding $1000"
                )
                return redirect("cart:checkout")
        elif payment_method == "Wallet Payment":
            if not withdraw_from_wallet(user, Decimal(total_amount)):
                request.session["message"] = "Insufficient Balance in Wallet"
                return redirect("cart:checkout")

        try:
            delivery_address = UserAddress.objects.get(id=address_id)
            address = DeliveyAddress.objects.create(
                name=delivery_address.name,
                phone=delivery_address.phone,
                country=delivery_address.country,
                state=delivery_address.state,
                city=delivery_address.city,
                landmark=delivery_address.landmark,
            )
            address.save()
        except ObjectDoesNotExist:
            return redirect("cart:checkout")

        if "discount_percentage" in request.session:
            discount_percentage = request.session.get("discount_percentage")
        else:
            discount_percentage = 0

        if "coupon_id" in request.session:
            coupon_id = request.session.get("coupon_id")
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                if coupon.limit == 0 or coupon.expiry_date < timezone.now().date():
                    request.session["message"] = "Invalid Coupon"
                    request.session.pop("discount_percentage", None)
                    request.session.pop("coupon_code", None)
                    request.session.pop("coupon_id", None)
                    return redirect("cart:checkout")
                else:
                    coupon.limit -= 1
                    coupon.save()
                    coupon_usage = CouponUsage.objects.create(coupon=coupon, user=user)
                    coupon_usage.save()
            except ObjectDoesNotExist:
                request.session["message"] = "Invalid Coupon"
                request.session.pop("discount_percentage", None)
                request.session.pop("coupon_code", None)
                request.session.pop("coupon_id", None)
                return redirect("cart:checkout")

        for item in ordered_products:
            product = Product.objects.get(id=item.product.id)
            product.stock = product.stock - item.quantity
            product.save()

            ordered_items = Orders.objects.create(
                user=user,
                ordered_date=ordered_date,
                payment_method=payment_method,
                address=address,
                discount_amt=item.total
                * (Decimal(discount_percentage) / Decimal("100")),
                product=product,
                product_price=product.price,
                product_qty=item.quantity,
            )
            ordered_items.save()

        request.session.pop("discount_percentage", None)
        request.session.pop("coupon_code", None)
        request.session.pop("coupon_id", None)
        CartItems.objects.filter(user=user_id).delete()

        if payment_method == "Online Payment":
            return HttpResponse(status=200)

        return redirect("cart:order_success")
    return redirect("cart:checkout")


# Order Success Page
@login_required(login_url="authentication:signin")
def order_success(request):
    return render(request, "user/order_success.html")


# Order Status updation
@login_required(login_url="authentication:signin")
def order_status(request, order_id, status):
    previous_url = request.META.get("HTTP_REFERER")
    try:
        item = Orders.objects.get(id=order_id)
        user = item.user
        amount = item.total
        purchased_qty = item.product_qty
        product_id = item.product.id

        if status == "Delivered":
            item.delivered_date = date.today()
        elif status == "Returned":
            item.return_status = None
            # Add amount of Returned product to wallet
            description = "Returned Product Amount Credited"
            update_wallet(user, amount, description)
            # Increase the product stock
            update_product_stock(purchased_qty, product_id)
        elif status == "Cancelled":
            # Add amount of Cancelled product to wallet if payment method is ("Online Payment" or "Wallet Payment")
            if item.payment_method in ["Online Payment", "Wallet Payment"]:
                description = "Cancelled Product Amount Credited"
                update_wallet(user, amount, description)
            # Increase the product stock
            update_product_stock(purchased_qty, product_id)
        if status in ["Requested Return", "Return request rejected"]:
            item.return_status = status
        else:
            item.status = status

        item.save()
    except ObjectDoesNotExist:
        return redirect(previous_url)
    return redirect(previous_url)
