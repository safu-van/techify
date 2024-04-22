from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from category.models import Category
from utils.utils import validate_image


# Category Block/Unblock
@login_required(login_url="authentication:signin")
def category_action(request, category_id):
    if request.user.is_superuser:
        try:
            category = Category.objects.get(id=category_id)
            if category.is_available:
                category.is_available = False
            else:
                category.is_available = True
            category.save()
        except ObjectDoesNotExist:
            return redirect("admin_techify:category_management")
        return redirect("admin_techify:category_management")
    return redirect("home:home_page")


# Add Category
@login_required(login_url="authentication:signin")
def add_category(request):
    if request.user.is_superuser:
        # category image validation error message
        if "message" in request.session:
            message = request.session.pop("message")
        else:
            message = None

        if request.method == "POST":
            category_name = request.POST.get("category_name")
            category_img = request.FILES.get("category_image")

            if Category.objects.filter(name__iexact=category_name).exists():
                category_exists = True
                return render(
                    request,
                    "admin/add_category.html",
                    {"category_exists": category_exists},
                )
            if not validate_image(category_img):
                request.session["message"] = "image_not_valid"
                return redirect("category:add_category")

            add_category = Category.objects.create(
                name=category_name, image=category_img
            )
            add_category.save()

            return redirect("admin_techify:category_management")
        return render(request, "custom_admin/add_category.html", {"message": message})
    return redirect("home:home_page")


# Edit Category
@login_required(login_url="authentication:signin")
def edit_category(request, category_id):
    if request.user.is_superuser:
        try:
            edit_category = Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return redirect("admin_techify:category_management")

        # category image validation error message
        if "message" in request.session:
            message = request.session.pop("message")
        else:
            message = None

        if request.method == "POST":
            category_name = request.POST.get("category_name")
            category_img = request.FILES.get("category_image")

            url = reverse("category:edit_category", kwargs={"category_id": category_id})

            if (
                Category.objects.filter(name__iexact=category_name)
                .exclude(name=edit_category.name)
                .exists()
            ):
                category_exists = True
                context = {
                    "category_exists": category_exists,
                    "edit_category": edit_category,
                }
                return render(request, "custom_admin/edit_category.html", context)

            edit_category.name = category_name
            if category_img:
                if not validate_image(category_img):
                    request.session["message"] = "image_not_valid"
                    return redirect(url)
                edit_category.image = category_img
            edit_category.save()

            return redirect("admin_techify:category_management")
        context = {"edit_category": edit_category, "message": message}
        return render(request, "custom_admin/edit_category.html", context)
    return redirect("home:home_page")
