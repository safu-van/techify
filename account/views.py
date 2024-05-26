import random
import string
from io import BytesIO

from xhtml2pdf import pisa

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.paginator import Paginator

from authentication.models import User
from account.models import UserAddress, Wallet, WalletTransaction
from cart.models import Orders


# Account Settings
@login_required(login_url="authentication:signin")
def account_settings(request):
    user_id = request.user.id
    message = False
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect("authentication:signin")

    if request.method == "POST":
        name = request.POST.get("name")
        user.name = name
        user.save()
        message = "name_updated"

    context = {"user": user, "message": message}
    return render(request, "user/account.html", context)


# Generate Referral code
@login_required(login_url="authentication:signin")
def generate_referral_code(request):
    user_id = request.user.id
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect("authentication:signin")

    while True:
        characters = string.ascii_letters + string.digits
        referral_code = "".join(random.choice(characters) for _ in range(8))

        if not User.objects.filter(referral_code=referral_code).exists():
            break

    user.referral_code = referral_code
    user.save()
    return redirect("account:account_settings")


# Orders
@login_required(login_url="authentication:signin")
def orders(request):
    user_id = request.user.id
    ordered_products = (
        Orders.objects.filter(user=user_id)
        .select_related("address", "product")
        .order_by("-id")
    )
    paginator = Paginator(ordered_products, 5)
    page_number = request.GET.get("page")
    ordered_obj = paginator.get_page(page_number)
    return render(request, "user/list_orders.html", {"ordered_obj": ordered_obj})


# Order Details
@login_required(login_url="authentication:signin")
def order_details(request, order_id):
    try:
        order = Orders.objects.get(id=order_id)
        return_order = False
        if order.status == "Delivered":
            delivered_date = order.delivered_date
            today_date = timezone.now().date()
            difference = (today_date - delivered_date).days
            if difference <= 7:
                return_order = True

        context = {
            "order": order,
            "return_order": return_order,
        }
        return render(request, "user/order_details.html", context)
    except ObjectDoesNotExist:
        return redirect("account:orders")


# Fetch User Addresses
@login_required(login_url="authentication:signin")
def address(request):
    user_id = request.user.id
    addresses = UserAddress.objects.filter(user=user_id)

    # Success message of Address Added/Edited
    if "message" in request.session:
        message = request.session.pop("message")
    else:
        message = False

    context = {
        "addresses": addresses,
        "message": message,
    }
    return render(request, "user/address.html", context)


# Remove Address
@login_required(login_url="authentication:signin")
def remove_address(request, address_id):
    previous_url = request.META.get("HTTP_REFERER")

    try:
        address = UserAddress.objects.get(id=address_id)
        address.delete()
    except ObjectDoesNotExist:
        return redirect(previous_url)

    return redirect(previous_url)


# Add Address
@login_required(login_url="authentication:signin")
def add_address(request):
    previous_url = request.META.get("HTTP_REFERER")

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        landmark = request.POST.get("landmark")
        state = request.POST.get("state")
        country = request.POST.get("country")

        user_id = request.user.id
        previous_url = request.POST.get("previous_url")

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return redirect("authentication:signin")

        add_address = UserAddress.objects.create(
            user=user,
            name=name,
            phone=phone,
            city=city,
            landmark=landmark,
            state=state,
            country=country,
        )
        add_address.save()
        request.session["message"] = "address_added"

        return redirect(previous_url)

    return render(request, "user/add_address.html", {"previous_url": previous_url})


# Edit Address
@login_required(login_url="authentication:signin")
def edit_address(request, address_id):
    previous_url = request.META.get("HTTP_REFERER")

    try:
        address = UserAddress.objects.get(id=address_id)
    except ObjectDoesNotExist:
        return redirect(previous_url)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        landmark = request.POST.get("landmark")
        state = request.POST.get("state")
        country = request.POST.get("country")
        previous_url = request.POST.get("previous_url")

        address.name = name
        address.phone = phone
        address.city = city
        address.landmark = landmark
        address.state = state
        address.country = country
        address.save()
        request.session["message"] = "address_edited"

        return redirect(previous_url)

    context = {
        "address": address,
        "previous_url": previous_url,
    }
    return render(request, "user/edit_address.html", context)


# Wallet
@login_required(login_url="authentication:signin")
def wallet(request):
    user = request.user.id
    try:
        if Wallet.objects.filter(user=user).exists():
            wallet = Wallet.objects.get(user=user)
            amount = wallet.amount
            transactions = WalletTransaction.objects.filter(wallet=wallet).order_by(
                "-id"
            )
            paginator = Paginator(transactions, 5)
            page_number = request.GET.get("page")
            transaction_obj = paginator.get_page(page_number)
        else:
            amount = 0.0
            transaction_obj = False
    except ObjectDoesNotExist:
        return redirect("authentication:signin")
    context = {
        "amount": amount,
        "transaction_obj": transaction_obj,
    }
    return render(request, "user/wallet.html", context)


# Change Password
@login_required(login_url="authentication:signin")
def change_password(request):
    message = False
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        user_id = request.user.id

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return redirect("authentication:signin")

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            message = "password_changed"
        else:
            message = "invalid_password"

    return render(request, "user/change_password.html", {"message": message})


# Download Product Invoice (PDF)
@login_required(login_url="authentication:signin")
def download_product_invoice(request, order_id):
    try:
        order = Orders.objects.get(id=order_id)
    except Orders.DoesNotExist:
        return HttpResponse("Order not found", status=404)

    context = {"order": order}
    template = get_template("user/invoice.html")
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if pdf:
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice_{order_id}.pdf"'
        )
        return response
    else:
        return HttpResponse("Error generating PDF", status=500)
