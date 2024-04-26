from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.urls import reverse

from product.models import Product, ProductDetails
from category.models import Category
from brand.models import Brand
from utils.utils import validate_image


# List Products
def product_list(request):
    if request.method == "POST":
        sort_by = request.POST.get("sortby")

        if sort_by == "Price: low to high":
            products = Product.objects.filter(
                is_available=True, category__is_available=True, brand__is_available=True
            ).order_by("price")
        elif sort_by == "Price: high to low":
            products = Product.objects.filter(
                is_available=True, category__is_available=True, brand__is_available=True
            ).order_by("-price")
        elif sort_by == "New Arrivals":
            products = Product.objects.filter(
                is_available=True, category__is_available=True, brand__is_available=True
            ).order_by("-id")
    else:
        products = Product.objects.filter(
            is_available=True, category__is_available=True, brand__is_available=True
        ).order_by("id")

    brands = Brand.objects.filter(is_available=True).annotate(
        product_count=Count("product")
    )
    categories = Category.objects.filter(is_available=True).annotate(
        product_count=Count("product")
    )

    context = {
        "products": products,
        "brands": brands,
        "categories": categories,
    }
    return render(request, "user/product_list.html", context)


# List filtered products
def filtered_products(request):
    if request.method == "POST":
        selected_categories = [
            int(cat_id) for cat_id in request.POST.getlist("categories")
        ]
        selected_brands = [int(brand_id) for brand_id in request.POST.getlist("brands")]

        products = Product.objects.filter(
            Q(category__id__in=selected_categories) | Q(brand__id__in=selected_brands)
        ).distinct()

        brands = Brand.objects.filter(is_available=True).annotate(
            product_count=Count("product")
        )
        categories = Category.objects.filter(is_available=True).annotate(
            product_count=Count("product")
        )

        context = {
            "products": products,
            "brands": brands,
            "categories": categories,
            "selected_brands": selected_brands,
            "selected_categories": selected_categories,
        }
    return render(request, "user/product_list.html", context)


# Search Products by query
def search_products(request):
    if request.method == "POST":
        search_query = request.POST.get("query")
        products = Product.objects.filter(
            name__icontains=search_query, is_available=True, brand__is_available=True
        ).exclude(category__is_available=False)
        return render(request, "user/product_list.html", {"products": products})


# List Products Based On Category
def category_product(request, category_id):
    products = Product.objects.filter(
        category=category_id, brand__is_available=True
    ).exclude(is_available=False)
    return render(request, "user/product_list.html", {"products": products})


# Product Individual View
def product_view(request, product_id):
    previous_url = request.META.get("HTTP_REFERER")
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return redirect(previous_url)

    if product.is_available:
        product_details = ProductDetails.objects.get(product=product)
        category = product.category
        related_products = Product.objects.filter(
            category=category, is_available=True, brand__is_available=True
        ).exclude(id=product_id)

        context = {
            "product": product,
            "product_details": product_details,
            "related_products": related_products,
        }
        return render(request, "user/product.html", context)
    return redirect("home:home_page")


# Add Product
@login_required(login_url="authentication:signin")
def add_product(request):
    if request.user.is_superuser:
        categories = Category.objects.all()
        brands = Brand.objects.all()

        # Product image validation error message
        if "message" in request.session:
            message = request.session.pop("message")
        else:
            message = None

        if request.method == "POST":
            name = request.POST.get("product_name")
            category_name = request.POST.get("category")
            brand_name = request.POST.get("brand")
            stock = request.POST.get("stock")
            price = request.POST.get("price")
            description = request.POST.get("description")
            additional_info = request.POST.get("additional_information")
            thumbnail = request.FILES.get("thumbnail")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")

            if not all(validate_image(image) for image in [thumbnail, image2, image3]):
                request.session["message"] = "image_not_valid"
                return redirect("product:add_product")

            category = Category.objects.get(name=category_name)
            brand = Brand.objects.get(name=brand_name)

            product = Product.objects.create(
                name=name,
                price=price,
                stock=stock,
                category=category,
                brand=brand,
                thumbnail=thumbnail,
                image2=image2,
                image3=image3,
            )
            product.save()

            product_details = ProductDetails.objects.create(
                product=product,
                description=description,
                additional_information=additional_info,
            )
            product_details.save()

            return redirect("admin_techify:product_management")
        context = {
            "categories": categories,
            "brands": brands,
            "message": message,
        }
        return render(request, "custom_admin/add_product.html", context)
    return redirect("home:home_page")


# Product Block/Unblock
@login_required(login_url="authentication:signin")
def product_action(request, product_id):
    if request.user.is_superuser:
        try:
            product = Product.objects.get(id=product_id)
            if product.is_available:
                product.is_available = False
            else:
                product.is_available = True
            product.save()
        except ObjectDoesNotExist:
            return redirect("admin_techify:product_management")
        return redirect("admin_techify:product_management")
    return redirect("home:home_page")


# Edit Product
@login_required(login_url="authentication:signin")
def edit_product(request, product_id):
    if request.user.is_superuser:
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return redirect("admin_techify:product_management")
        categories = Category.objects.all()
        brands = Brand.objects.all()
        product_details = product.product_details

        # Product image validation error message
        if "message" in request.session:
            message = request.session.pop("message")
        else:
            message = None

        if request.method == "POST":
            name = request.POST.get("product_name")
            category_name = request.POST.get("category")
            brand_name = request.POST.get("brand")
            stock = request.POST.get("stock")
            price = request.POST.get("price")
            description = request.POST.get("description")
            additional_info = request.POST.get("additional_information")
            thumbnail = request.FILES.get("thumbnail")
            image2 = request.FILES.get("image2")
            image3 = request.FILES.get("image3")

            product.name = name
            product.stock = stock
            product.price = price
            category = Category.objects.get(name=category_name)
            product.category = category
            brand = Brand.objects.get(name=brand_name)
            product.brand = brand
            product_details.description = description
            product_details.additional_information = additional_info
            product_details.save()

            url = reverse("product:edit_product", kwargs={"product_id": product_id})

            if thumbnail:
                if not validate_image(thumbnail):
                    request.session["message"] = "image_not_valid"
                    return redirect(url)
                product.thumbnail = thumbnail
            if image2:
                if not validate_image(image2):
                    request.session["message"] = "image_not_valid"
                    return redirect(url)
                product.image2 = image2
            if image3:
                if not validate_image(image3):
                    request.session["message"] = "image_not_valid"
                    return redirect(url)
                product.image3 = image3

            product.save()

            return redirect("admin_techify:product_management")

        context = {
            "product": product,
            "categories": categories,
            "brands": brands,
            "product_details": product_details,
            "message": message,
        }
        return render(request, "custom_admin/edit_product.html", context)
    return redirect("home:home_page")
