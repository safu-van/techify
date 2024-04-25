from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from coupon.models import Coupon


# Add Coupon
@login_required(login_url="authentication:signin")
def add_coupon(request):
    if request.user.is_superuser:
        if request.method == "POST":
            coupon_name = request.POST.get("coupon_name")
            coupon_code = request.POST.get("coupon_code")
            discount_percentage = request.POST.get("discount")
            user_limit = request.POST.get("user_limit")
            expiry_date = request.POST.get("expiry_date")

            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

            if Coupon.objects.filter(name__iexact=coupon_name).exists():
                error_message = "Coupon name already exists."
                return render(
                    request, "admin/add_coupon.html", {"error_message": error_message}
                )

            if Coupon.objects.filter(code__iexact=coupon_code).exists():
                error_message = "Coupon code already exists."
                return render(
                    request, "admin/add_coupon.html", {"error_message": error_message}
                )

            new_coupon = Coupon.objects.create(
                name=coupon_name,
                code=coupon_code,
                discount_percentage=discount_percentage,
                limit=user_limit,
                expiry_date=expiry_date,
            )
            new_coupon.save()
            return redirect("admin_techify:coupon_management")
        return render(request, "custom_admin/add_coupon.html")
    return redirect("home:home_page")


# Edit Coupon
@login_required(login_url="authentication:signin")
def edit_coupon(request, coupon_id):
    if request.user.is_superuser:
        try:
            update_coupon = Coupon.objects.get(id=coupon_id)
            expiry_date = update_coupon.expiry_date.strftime("%Y-%m-%d")
        except ObjectDoesNotExist:
            return redirect("admin_techify:coupon_management")

        if request.method == "POST":
            coupon_name = request.POST.get("coupon_name")
            coupon_code = request.POST.get("coupon_code")
            discount_percentage = request.POST.get("discount")
            user_limit = request.POST.get("user_limit")
            expiry_date = request.POST.get("expiry_date")

            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

            if (
                Coupon.objects.filter(name__iexact=coupon_name)
                .exclude(name=update_coupon.name)
                .exists()
            ):
                error_message = "Coupon name already exists."
                context = {
                    "error_message": error_message,
                    "update_coupon": update_coupon,
                }
                return render(request, "custom_admin/edit_coupon.html", context)

            if (
                Coupon.objects.filter(code__iexact=coupon_code)
                .exclude(code=update_coupon.code)
                .exists()
            ):
                error_message = "Coupon code already exists."
                context = {
                    "error_message": error_message,
                    "update_coupon": update_coupon,
                }
                return render(request, "custom_admin/edit_coupon.html", context)

            update_coupon.name = coupon_name
            update_coupon.code = coupon_code
            update_coupon.discount_percentage = discount_percentage
            update_coupon.limit = user_limit
            update_coupon.expiry_date = expiry_date
            update_coupon.save()

            return redirect("admin_techify:coupon_management")

        context = {"update_coupon": update_coupon, "expiry_date": expiry_date}
        return render(request, "custom_admin/edit_coupon.html", context)
    return redirect("home:home_page")


# Delete Coupon
@login_required(login_url="authentication:signin")
def remove_coupon(request, coupon_id):
    if request.user.is_superuser:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            coupon.delete()
        except ObjectDoesNotExist:
            return redirect("admin_techify:coupon_management")
        return redirect("admin_techify:coupon_management")
    return redirect("home:home_page")
