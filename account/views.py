from django.shortcuts import render, redirect

from authentication.models import User
from account.models import UserAddress, Orders

from datetime import date


# Create your views here.


def account(request):
    if request.user.is_authenticated:
        id = request.user.id
        user = User.objects.get(id=id)
        if request.method == "POST":
            name = request.POST.get("name")
            user.full_name = name
            user.save()
        return render(request, "user/dashboard.html", {"user": user})
    return redirect("home:home_page")


def orders(request):
    user_id = request.user.id
    ordered_items = Orders.objects.filter(user=user_id).order_by("-id")
    return render(request, "user/list_orders.html", {"ordered_items": ordered_items})


def order_status(request, order_id, status):
    item = Orders.objects.get(id=order_id)
    item.status = status
    if status == "DELIVERD":
        item.deliverd_date = date.today()
    item.save()
    previous_url = request.META.get("HTTP_REFERER")
    return redirect(previous_url)


def address(request):
    user_id = request.user.id
    addressess = UserAddress.objects.filter(user=user_id, status=True)
    return render(request, "user/address.html", {"addressess": addressess})


def remove_address(request, address_id):
    address = UserAddress.objects.get(id=address_id)
    address.status = False
    address.save()
    previous_url = request.META.get("HTTP_REFERER")
    return redirect(previous_url)


def edit_address(request, address_id):
    user_id = request.user.id
    address = UserAddress.objects.get(id=address_id, user=user_id)
    previous_url = request.META.get("HTTP_REFERER")

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

        return redirect(url)

    context = {
        "address": address,
        "previous_url": previous_url,
    }
    return render(request, "user/edit_address.html", context)


def change_password(request):
    message = False
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        user_id = request.user.id

        user = User.objects.get(id=user_id)

        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
        else:
            message = True

    return render(request, "user/change_password.html", {"message": message})


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
        url = request.POST.get("previous_url")

        user = User.objects.get(id=user_id)
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

        return redirect(url)

    return render(request, "user/add_address.html", {"previous_url": previous_url})
