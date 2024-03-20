from django.shortcuts import render, redirect

from product.models import Product, ProductDetails
from category.models import Category


# List Products
def product_list(request):
    sort_by = request.GET.get("sortby")
    if sort_by == "A":
        products = (
            Product.objects.filter(is_available=True)
            .exclude(category__is_available=False)
            .order_by("price")
        )
        return render(request, "user/product_list.html", {"products": products})
    elif sort_by == "B":
        products = (
            Product.objects.filter(is_available=True)
            .exclude(category__is_available=False)
            .order_by("-price")
        )
        return render(request, "user/product_list.html", {"products": products})
    elif sort_by == "C":
        products = (
            Product.objects.filter(is_available=True)
            .exclude(category__is_available=False)
            .order_by("id")
        )
        return render(request, "user/product_list.html", {"products": products})
    else:
        products = (
            Product.objects.filter(is_available=True)
            .exclude(category__is_available=False)
            .order_by("-id")
        )
    return render(request, "user/product_list.html", {"products": products})


# Product Individual View
def product_view(request, product_id):
    product = Product.objects.get(id=product_id)

    if product.is_available:
        product_details = ProductDetails.objects.get(product=product)
        category = product.category
        related_products = Product.objects.filter(category=category).exclude(
            id=product_id
        )

        context = {
            "product": product,
            "product_details": product_details,
            "related_products": related_products,
        }
        return render(request, "user/product.html", context)
    return redirect("home:home_page")


# List Products Based On Category
def category_product(request, category_id):
    products = Product.objects.filter(category=category_id).exclude(is_available=False)
    return render(request, "user/product_list.html", {"products": products})


# Add Product
def add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("product_name")
        category_name = request.POST.get("category")
        stock = request.POST.get("stock")
        price = request.POST.get("price")
        description = request.POST.get("description")
        additional_info = request.POST.get("additional_information")
        thumbnail = request.FILES.get("thumbnail")
        image2 = request.FILES.get("image2")
        image3 = request.FILES.get("image3")

        errors = {}
        if not name:
            errors["name"] = "Product name is required."
        if not category_name:
            errors["category_name"] = "Category is required."
        if not price.isdigit() or float(price) <= 0:
            errors["price"] = "Price must be a greater than 0."
        if not stock.isdigit() or int(stock) < 0:
            errors["stock"] = "Stock must be a be 0 or greater than 0."
        if not description:
            errors["description"] = "Description is required."
        if not additional_info:
            errors["additional_info"] = "Additional information is required."
        if not thumbnail or not image2 or not image3:
            errors["images"] = "Please upload three images."

        if errors:
            context = {"errors": errors, "categories": categories}
            return render(request, "admin/add_product.html", context)

        category = Category.objects.get(name=category_name)

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            category=category,
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
    return render(request, "admin/add_product.html", {"categories": categories})


# Product Block/Unblock
def product_action(request, product_id):
    product = Product.objects.get(id=product_id)

    if product.is_available:
        product.is_available = False
    else:
        product.is_available = True

    product.save()
    return redirect("admin_techify:product_management")


# Edit Product
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    product_details = product.product_details

    if request.method == "POST":
        name = request.POST.get("product_name")
        category_name = request.POST.get("category")
        stock = request.POST.get("stock")
        price = request.POST.get("price")
        description = request.POST.get("description")
        additional_info = request.POST.get("additional_information")
        thumbnail = request.FILES.get("thumbnail")
        image2 = request.FILES.get("image2")
        image3 = request.FILES.get("image3")

        errors = {}
        if not name:
            errors["name"] = "Product name is required."
        if not category_name:
            errors["category_name"] = "Category is required."
        if not price.replace(".", "", 1).isdigit() or float(price) <= 0:
            errors["price"] = "Price must be a greater than 0."
        if not stock.isdigit() or int(stock) < 0:
            errors["stock"] = "Stock must be a be 0 or greater than 0."
        if not description:
            errors["description"] = "Description is required."
        if not additional_info:
            errors["additional_info"] = "Additional information is required."

        if errors:
            context = {
                "product": product,
                "categories": categories,
                "product_details": product_details,
                "errors": errors,
            }
            return render(request, "admin/edit_product.html", context)

        product.name = name
        product.stock = stock
        product.price = price

        category = Category.objects.get(name=category_name)
        product.category = category

        product_details.description = description
        product_details.additional_information = additional_info
        product_details.save()

        if thumbnail:
            product.thumbnail = thumbnail
        if image2:
            product.image2 = image2
        if image3:
            product.image3 = image3

        product.save()

        return redirect("admin_techify:product_management")

    context = {
        "product": product,
        "categories": categories,
        "product_details": product_details,
    }
    return render(request, "admin/edit_product.html", context)
