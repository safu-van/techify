from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from offer.models import Offer


# Add Offer
@login_required(login_url="authentication:signin")
def add_offer(request):
    if request.user.is_superuser:
        if request.method == "POST":
            offer_name = request.POST.get("offer_name")
            discount = request.POST.get("discount")
            active_date = request.POST.get("active_date")
            expiry_date = request.POST.get("expiry_date")

            active_date = datetime.strptime(active_date, "%Y-%m-%d").date()
            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

            if Offer.objects.filter(name__iexact=offer_name).exists():
                error_message = "Offer name already exists."
                return render(
                    request, "admin/add_offer.html", {"error_message": error_message}
                )

            new_offer = Offer.objects.create(
                name=offer_name,
                discount=discount,
                active_date=active_date,
                expiry_date=expiry_date,
            )
            new_offer.save()
            return redirect("admin_techify:offer_management")
        return render(request, "custom_admin/add_offer.html")
    return redirect("home:home_page")


# Edit Offer
@login_required(login_url="authentication:signin")
def edit_offer(request, offer_id):
    if request.user.is_superuser:
        try:
            update_offer = Offer.objects.get(id=offer_id)
            active_date = update_offer.active_date.strftime("%Y-%m-%d")
            expiry_date = update_offer.expiry_date.strftime("%Y-%m-%d")
        except ObjectDoesNotExist:
            return redirect("admin_techify:offer_management")

        if request.method == "POST":
            offer_name = request.POST.get("offer_name")
            discount = request.POST.get("discount")
            active_date = request.POST.get("active_date")
            expiry_date = request.POST.get("expiry_date")

            active_date = datetime.strptime(active_date, "%Y-%m-%d").date()
            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

            if (
                Offer.objects.filter(name__iexact=offer_name)
                .exclude(name=update_offer.name)
                .exists()
            ):
                error_message = "Offer name already exists."
                context = {"error_message": error_message, "offer": update_offer}
                return render(request, "custom_admin/add_offer.html", context)

            update_offer.name = offer_name
            update_offer.discount = discount
            update_offer.active_date = active_date
            update_offer.expiry_date = expiry_date
            update_offer.save()

            return redirect("admin_techify:offer_management")

        context = {
            "offer": update_offer,
            "active_date": active_date,
            "expiry_date": expiry_date,
        }
        return render(request, "custom_admin/edit_offer.html", context)
    return redirect("home:home_page")


# Delete Offer
@login_required(login_url="authentication:signin")
def remove_offer(request, offer_id):
    if request.user.is_superuser:
        try:
            offer = Offer.objects.get(id=offer_id)
            offer.delete()
        except ObjectDoesNotExist:
            return redirect("admin_techify:offer_management")
        return redirect("admin_techify:offer_management")
    return redirect("home:home_page")
