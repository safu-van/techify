from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from brand.models import Brand


# Add brand
@login_required(login_url="authentication:signin")
def add_brand(request):
    if request.user.is_superuser:
        if request.method == "POST":
            name = request.POST.get("brand_name")

            if Brand.objects.filter(name__iexact=name).exists():
                brand_exists = True
                return render(
                    request,
                    "custom_admin/add_brand.html",
                    {"brand_exists": brand_exists},
                )

            new_brand = Brand.objects.create(name=name)
            new_brand.save()
            return redirect("admin_techify:brand_management")
        return render(request, "custom_admin/add_brand.html")
    return redirect("home:home_page")


# Edit brand
@login_required(login_url="authentication:signin")
def edit_brand(request, brand_id):
    if request.user.is_superuser:
        try:
            update_brand = Brand.objects.get(id=brand_id)
        except ObjectDoesNotExist:
            return redirect("admin_techify:brand_management")

        if request.method == "POST":
            name = request.POST.get("brand_name")

            if (
                Brand.objects.filter(name__iexact=name)
                .exclude(name=update_brand.name)
                .exists()
            ):
                brand_exists = True
                context = {
                    "brand_exists": brand_exists,
                    "brand": update_brand,
                }
                return render(request, "custom_admin/edit_brand.html", context)

            update_brand.name = name
            update_brand.save()
            return redirect("admin_techify:brand_management")
        return render(request, "custom_admin/edit_brand.html", {"brand": update_brand})
    return redirect("home:home_page")


# Brand Block/Unblock
@login_required(login_url="authentication:signin")
def brand_action(request, brand_id):
    if request.user.is_superuser:
        try:
            brand = Brand.objects.get(id=brand_id)
            if brand.is_available:
                brand.is_available = False
            else:
                brand.is_available = True
            brand.save()
        except ObjectDoesNotExist:
            return redirect("admin_techify:brand_management")
        return redirect("admin_techify:brand_management")
    return redirect("home:home_page")
