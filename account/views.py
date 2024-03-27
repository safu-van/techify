from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from authentication.models import User
from account.models import UserAddress
from cart.models import Orders

from datetime import date


# Account Settings
@login_required(login_url="authentication:signin")
def account_settings(request):
    user_id = request.user.id
    message = False
    try:
        user = User.objects.get(id=user_id)
        if request.method == "POST":
            name = request.POST.get("name")
            user.name = name
            user.save()
            message = "name_updated"
    except ObjectDoesNotExist:
        pass

    context = {
        "user": user,
        "message": message
    }    
    return render(request, "user/account.html", context)


# My Orders
@login_required(login_url="authentication:signin")
def orders(request):
    user_id = request.user.id
    ordered_items = Orders.objects.filter(user=user_id).order_by("-id")

    return render(request, "user/list_orders.html", {"ordered_items": ordered_items})


# Order Status updation
@login_required(login_url="authentication:signin")
def order_status(request, order_id, status):
    try:
        previous_url = request.META.get("HTTP_REFERER")
    except Exception:
        pass

    try:
        item = Orders.objects.get(id=order_id)
        item.status = status
        if status == "DELIVERED":
            item.delivered_date = date.today()
        item.save()
    except ObjectDoesNotExist:
        pass

    return redirect(previous_url)


# Fetch User Addresses
@login_required(login_url="authentication:signin")
def address(request):
    user_id = request.user.id
    addresses = UserAddress.objects.filter(user=user_id, status=True)

    if 'message' in request.session:
        message = request.session.pop('message')
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
    try:
        previous_url = request.META.get("HTTP_REFERER")
    except Exception:
        pass

    try:
        address = UserAddress.objects.get(id=address_id)
        address.status = False
        address.save()
    except ObjectDoesNotExist:
        pass

    return redirect(previous_url)


# Add Address
@login_required(login_url="authentication:signin")
def add_address(request):
    try:
        previous_url = request.META.get("HTTP_REFERER")
    except Exception:
        pass
    
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        landmark = request.POST.get("landmark")
        state = request.POST.get("state")
        country = request.POST.get("country")
        user_id = request.user.id
        url = request.POST.get("previous_url")

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            pass
        
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
        request.session['message'] = "address_added"

        return redirect(url)

    return render(request, "user/add_address.html", {"previous_url": previous_url})


# Edit Address
@login_required(login_url="authentication:signin")
def edit_address(request, address_id):
    try:
        previous_url = request.META.get("HTTP_REFERER")
    except Exception:
        pass

    try:
        address = UserAddress.objects.get(id=address_id)
    except ObjectDoesNotExist:
        pass

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        landmark = request.POST.get("landmark")
        state = request.POST.get("state")
        country = request.POST.get("country")
        url = request.POST.get("previous_url")

        address.name = name
        address.phone = phone
        address.city = city
        address.landmark = landmark
        address.state = state
        address.country = country
        address.save()
        request.session['message'] = "address_edited"

        return redirect(url)

    context = {
        "address": address,
        "previous_url": previous_url,
    }
    return render(request, "user/edit_address.html", context)


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
            pass

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            message = "password_changed"
        else:
            message = "invalid_password"

    return render(request, "user/change_password.html", {"message": message})

