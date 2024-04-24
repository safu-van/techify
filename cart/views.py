import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from cart.models import CartItems, Orders, DeliveyAddress
from product.models import Product
from authentication.models import User
from account.models import UserAddress, Wallet
from coupon.models import Coupon, CouponUsage

from datetime import date
from django.utils import timezone
from decimal import Decimal


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
        total_price = product_price * product_quantity
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
    total = float(product.price) * int(quantity)

    if CartItems.objects.filter(product=product_id, user=user_id).exists():
        response_data["message"] = "Item already in cart"
    else:
        if stock_of_product > 0 and int(quantity) <= stock_of_product:
            try:
                user = User.objects.get(id=user_id)
                new_item = CartItems.objects.create(
                    product=product, quantity=quantity, user=user, total=total
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
            item.total = item.product.price * value
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


# To Check product stock
def check_product_stock(request):
    user_id = request.user.id
    products = CartItems.objects.filter(user=user_id)

    for product in products:
        qty = product.quantity
        stock = product.product.stock
        product_name = product.product.name
        if stock < qty:
            request.session["message"] = (
                f"Sorry, We only have { stock } quantity of { product_name }."
            )
            return False
    return True


# Checkout
@login_required(login_url="authentication:signin")
def checkout(request):
    user_id = request.user.id
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect("authentication:signin")

    if not check_product_stock(request):
        return redirect("cart:cart")

    if request.method == "POST":
        if "coupon_code" in request.POST:
            coupon_code = request.POST.get("coupon_code")
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.limit == 0 or coupon.expiry_date < timezone.now().date():
                    request.session["message"] = "Invalid_coupon"
                else:
                    if CouponUsage.objects.filter(coupon=coupon, user=user).exists():
                        request.session["message"] = "coupon_already_used"
                    else:
                        discount_percentage = coupon.discount_percentage
                        request.session["discount_percentage"] = discount_percentage
                        request.session["coupon_code"] = coupon_code
                        request.session["coupon_id"] = coupon.id
                return redirect("cart:checkout")
            except ObjectDoesNotExist:
                request.session["message"] = "Invalid_coupon"
                request.session.pop("discount_percentage", None)
                request.session.pop("coupon_code", None)
                request.session.pop("coupon_id", None)

        elif "selectedAddressId" in request.POST:
            if not check_product_stock(request):
                return redirect("cart:cart")

            address_id = request.POST.get("selectedAddressId")
            payment_method = request.POST.get("payment_method")
            ordered_date = date.today()
            ordered_products = CartItems.objects.filter(user=user_id)

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
                    if coupon.limit == 0:
                        request.session["message"] = "Invalid_coupon"
                        request.session.pop("discount_percentage", None)
                        request.session.pop("coupon_code", None)
                        request.session.pop("coupon_id", None)
                        return redirect("cart:checkout")
                    else:
                        coupon.limit -= 1
                        coupon.save()
                        coupon_usage = CouponUsage.objects.create(
                            coupon=coupon, user=user
                        )
                        coupon_usage.save()
                except ObjectDoesNotExist:
                    request.session["message"] = "Invalid_coupon"
                    request.session.pop("discount_percentage", None)
                    request.session.pop("coupon_code", None)
                    request.session.pop("coupon_id", None)

            for item in ordered_products:
                product = Product.objects.get(id=item.product.id)
                product.stock = product.stock - item.quantity
                product.save()

                ordered_items = Orders.objects.create(
                    user=user,
                    ordered_date=ordered_date,
                    payment_method=payment_method,
                    address=address,
                    sub_total=item.total,
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

            return redirect("cart:order_success")

    # Message of Address (Added/Edited) or coupon message
    if "message" in request.session:
        message = request.session.pop("message")
    else:
        message = False

    addresses = UserAddress.objects.filter(user=user_id)
    products = CartItems.objects.filter(user=user_id).annotate(sub_total=Sum("total"))
    sub_total = products.aggregate(sub_total=Sum("total"))["sub_total"]
    total = sub_total

    if "discount_percentage" in request.session:
        discount_percentage = request.session.get("discount_percentage")
        discount_amt = sub_total * (Decimal(discount_percentage) / Decimal("100"))
        total = sub_total - discount_amt
    else:
        discount_amt = False

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


# Order Success Page
@login_required(login_url="authentication:signin")
def order_success(request):
    return render(request, "user/order_success.html")


# Order Status updation
def order_status(request, order_id, status):
    previous_url = request.META.get("HTTP_REFERER")

    try:
        item = Orders.objects.get(id=order_id)
        item.status = status
        if status == "Delivered":
            item.delivered_date = date.today()
        elif status == "Returned":
            user = User.objects.get(id=request.user.id)
            amount = item.total
            if Wallet.objects.filter(user=user).exists():
                wallet = Wallet.objects.get(user=user)
                wallet.amount += amount
            else:
                wallet = Wallet.objects.create(user=user, amount=amount)
            wallet.save()
            purchased_qty = item.product_qty
            product = Product.objects.get(id=item.product.id)
            product.stock += purchased_qty
            product.save()
        elif status == "Cancelled":
            purchased_qty = item.product_qty
            product = Product.objects.get(id=item.product.id)
            product.stock += purchased_qty
            product.save()
        item.save()
    except ObjectDoesNotExist:
        return redirect(previous_url)
    return redirect(previous_url)
