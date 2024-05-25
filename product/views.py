from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator

from product.models import Product, ProductDetails
from category.models import Category
from brand.models import Brand
from utils.utils import validate_image


# List Products
def product_list(request):
    products = Product.objects.filter(
        is_available=True, category__is_available=True, brand__is_available=True
    ).select_related('category', 'brand', 'offer').order_by('id')

    # Search products
    search_query = request.GET.get("query", None)
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Category wise products
    category_id = request.GET.get("category", None) 
    if category_id:
        products = products.filter(category__id=category_id)

    # Filter products
    selected_categories = [int(cat_id) for cat_id in request.GET.getlist("categories")]
    selected_brands = [int(brand_id) for brand_id in request.GET.getlist("brands")]
    if selected_categories or selected_brands:
        products = products.filter(
            Q(category__id__in=selected_categories) | Q(brand__id__in=selected_brands)
        ).distinct()

    # Sorting products
    sort_by = request.GET.get("sortby", None)
    if sort_by == "Price: low to high":
        products = products.order_by("p_price")
    elif sort_by == "Price: high to low":
        products = products.order_by("-p_price")
    elif sort_by == "New Arrivals":
        products = products.order_by("-id")

    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    product_obj = paginator.get_page(page_number)

    brands = Brand.objects.filter(is_available=True).annotate(
        product_count=Count("product")
    ).filter(product_count__gt=0)
    categories = Category.objects.filter(is_available=True).annotate(
        product_count=Count("product")
    ).filter(product_count__gt=0)

    context = {
        "product_obj": product_obj,
        "brands": brands,
        "categories": categories,
        "sort_by": sort_by,
        "category_id": category_id,
        "search_query": search_query,
        "selected_brands": selected_brands,
        "selected_categories": selected_categories,
    }
    return render(request, "user/product_list.html", context)


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
        ).exclude(id=product_id).select_related('category', 'offer')

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
                p_price=price,
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
            product.p_price = price
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
