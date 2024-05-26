from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime

from offer.models import Offer
from product.models import Product
from category.models import Category


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

            request.session["offer_message"] = f"{offer_name} Offer Added"

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

            request.session["offer_message"] = f"{offer_name} Offer Updated"

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


# Individual Product Offer
@login_required(login_url="authentication:signin")
def product_offer(request, product_id, offer_id):
    if request.user.is_superuser:
        try:
            product = Product.objects.get(id=product_id)
            offer = Offer.objects.get(id=offer_id)
            product.offer = offer
            product.save()
        except ObjectDoesNotExist:
            return redirect("admin_techify:product_management")
        return redirect("admin_techify:product_management")
    return redirect("home:home_page")


# Category Offer
@login_required(login_url="authentication:signin")
def category_offer(request, category_id, offer_id):
    if request.user.is_superuser:
        try:
            offer = Offer.objects.get(id=offer_id)
            category = Category.objects.get(id=category_id)
            flag = 0
            if Product.objects.filter(category=category_id):
                if Product.objects.filter(
                    category=category_id, offer__isnull=True
                ).exists():
                    Product.objects.filter(category=category_id, offer__isnull=True).update(
                        offer=offer
                    )
                    flag = 1
                product_with_offer = Product.objects.filter(
                    category=category_id, offer__isnull=False
                )
                if product_with_offer:
                    for product in product_with_offer:
                        if product.offer.discount < offer.discount:
                            product.offer = offer
                            product.save()
                            flag = 1
                if flag == 1:
                    category.offer = offer
                    category.save()
                else:
                    request.session["message"] = (
                        f"{category.name} category products already have offer which is greater than {offer.name}"
                    )
            else:
                request.session["message"] = (
                    f"{category.name} category doesn't have products"
                )
        except ObjectDoesNotExist:
            return redirect("admin_techify:category_management")
        return redirect("admin_techify:category_management")
    return redirect("home:home_page")


# Remove Product Offer
@login_required(login_url="authentication:signin")
def remove_product_offer(request, product_id):
    if request.user.is_superuser:
        try:
            product = Product.objects.get(id=product_id)
            product.offer = None
            product.save()
        except ObjectDoesNotExist:
            return redirect("admin_techify:product_management")
        return redirect("admin_techify:product_management")
    return redirect("home:home_page")


# Remove Category Offer
def remove_category_offer(request, category_id):
    if request.user.is_superuser:
        try:
            Product.objects.filter(category=category_id).update(offer=None)
            category = Category.objects.get(id=category_id)
            category.offer = None
            category.save()
        except ObjectDoesNotExist:
            return redirect("admin_techify:category_management")
        return redirect("admin_techify:category_management")
    return redirect("home:home_page")
