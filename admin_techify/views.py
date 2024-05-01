import calendar
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from xhtml2pdf import pisa

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponse

from category.models import Category
from brand.models import Brand
from authentication.models import User
from product.models import Product
from cart.models import Orders
from coupon.models import Coupon
from offer.models import Offer


# Admin Dashboard
@login_required(login_url="authentication:signin")
def admin_dashboard(request):
    if request.user.is_superuser:
        # Total Revenue
        total_orders = Orders.objects.filter(status="Delivered")
        total_revenue = sum(order.total for order in total_orders)
        # Monthly Revenue
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_orders = Orders.objects.filter(
            status="Delivered",
            ordered_date__month=current_month,
            ordered_date__year=current_year,
        )
        monthly_revenue = sum(order.total for order in monthly_orders)
        # Daily Revenue
        current_date = timezone.now().date()
        daily_orders = Orders.objects.filter(
            status="Delivered", ordered_date=current_date
        )
        daily_revenue = sum(order.total for order in daily_orders)
        # Total Sales
        total_sales = Orders.objects.filter(status="Delivered").count()
        # Top Selling Products
        top_selling_products = Product.objects.annotate(
            total_orders=Count("orders")
        ).order_by("-total_orders")[:7]
        context = {
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "daily_revenue": daily_revenue,
            "total_sales": total_sales,
            "top_products": top_selling_products,
        }
        return render(request, "custom_admin/index.html", context)
    return redirect("home:home_page")


# User Management
@login_required(login_url="authentication:signin")
def user_management(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True).order_by("-id")
        return render(request, "custom_admin/user.html", {"users": users})
    return redirect("home:home_page")


# Brand Management
@login_required(login_url="authentication:signin")
def brand_management(request):
    if request.user.is_superuser:
        brands = Brand.objects.annotate(products_count=Count("product")).order_by("-id")
        return render(request, "custom_admin/brand.html", {"brands": brands})
    return redirect("home:home_page")


# Category Management
@login_required(login_url="authentication:signin")
def category_management(request):
    if request.user.is_superuser:
        categories = Category.objects.annotate(
            products_count=Count("product")
        ).order_by("-id")
        offers = Offer.objects.filter(
            active_date__lte=timezone.now().date(),
            expiry_date__gte=timezone.now().date(),
        )
        context = {"categories": categories, "offers": offers}
        return render(request, "custom_admin/category.html", context)
    return redirect("home:home_page")


# Product Management
@login_required(login_url="authentication:signin")
def product_management(request):
    if request.user.is_superuser:
        products = Product.objects.all().order_by("-id")
        offers = Offer.objects.filter(
            active_date__lte=timezone.now().date(),
            expiry_date__gte=timezone.now().date(),
        )
        context = {"products": products, "offers": offers}
        return render(request, "custom_admin/product.html", context)
    return redirect("home:home_page")


# Order Management
@login_required(login_url="authentication:signin")
def order_management(request):
    if request.user.is_superuser:
        ordered_products = Orders.objects.all().order_by("-id")
        orders = []
        for item in ordered_products:
            order_id = item.id
            ordered_date = item.ordered_date
            total = item.total
            address_name = item.address.name
            status = item.status
            delivered_date = item.delivered_date
            product_image = item.product.thumbnail.url
            product_name = item.product.name
            orders.append(
                {
                    "order_id": order_id,
                    "ordered_date": ordered_date,
                    "total": total,
                    "address_name": address_name,
                    "status": status,
                    "delivered_date": delivered_date,
                    "product_image": product_image,
                    "product_name": product_name,
                }
            )
        return render(request, "custom_admin/orders.html", {"orders": orders})
    return redirect("home:home_page")


# Order Details
@login_required(login_url="authentication:signin")
def order_details(request, order_id):
    if request.user.is_superuser:
        try:
            order = Orders.objects.get(id=order_id)
            return render(request, "custom_admin/order_details.html", {"order": order})
        except ObjectDoesNotExist:
            return redirect("admin_techify:order_management")
    return redirect("home:home_page")


# Coupon Management
@login_required(login_url="authentication:signin")
def coupon_management(request):
    if request.user.is_superuser:
        coupons = Coupon.objects.annotate(users_used=Count("couponusage")).order_by(
            "-id"
        )
        return render(request, "custom_admin/coupon.html", {"coupons": coupons})
    return redirect("home:home_page")


# Sales Report
@login_required(login_url="authentication:signin")
def sales_report(request):
    if request.user.is_superuser:
        if request.method == "POST":
            time_interval = request.POST.get("time_interval")

            if time_interval == "Today":
                sales = Orders.objects.filter(
                    status="Delivered", delivered_date=datetime.now().date()
                )
                sales_count = sales.count()
                total_sales = sum(order.total for order in sales)
            elif time_interval == "Weekly":
                start_of_week = datetime.now().date() - timedelta(
                    days=datetime.now().weekday()
                )
                end_of_week = start_of_week + timedelta(days=6)
                sales = Orders.objects.filter(
                    status="Delivered",
                    delivered_date__range=[start_of_week, end_of_week],
                )
                sales_count = sales.count()
                total_sales = sum(order.total for order in sales)
            elif time_interval == "Monthly":
                start_of_month = datetime(
                    datetime.now().year, datetime.now().month, 1
                ).date()
                _, num_days = calendar.monthrange(
                    datetime.now().year, datetime.now().month
                )
                end_of_month = datetime(
                    datetime.now().year, datetime.now().month, num_days
                ).date()
                sales = Orders.objects.filter(
                    status="Delivered",
                    delivered_date__range=[start_of_month, end_of_month],
                )
                sales_count = sales.count()
                total_sales = sum(order.total for order in sales)
            elif time_interval == "Yearly":
                start_of_year = datetime(datetime.now().year, 1, 1).date()
                end_of_year = datetime(datetime.now().year, 12, 31).date()
                sales = Orders.objects.filter(
                    status="Delivered",
                    delivered_date__range=[start_of_year, end_of_year],
                )
                sales_count = sales.count()
                total_sales = sum(order.total for order in sales)
            else:
                start_date = request.POST.get("start_date")
                end_date = request.POST.get("end_date")
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                sales = Orders.objects.filter(
                    status="Delivered", delivered_date__range=[start_date, end_date]
                )
                sales_count = sales.count()
                total_sales = sum(order.total for order in sales)
            pdf_data = {
                "sales": sales,
                "sales_count": sales_count,
                "total_sales": total_sales,
            }
            html_content = render(
                request, "custom_admin/report.html", pdf_data
            ).content.decode("utf-8")
            context = {
                "sales": sales,
                "html_content": html_content,
                "live_view": True,
                "sales_count": sales_count,
                "total_sales": total_sales,
            }
            return render(request, "custom_admin/report.html", context)
        return render(request, "custom_admin/sales_report.html")
    return redirect("home:home_page")


# Download sales_report (PDF format)
@login_required(login_url="authentication:signin")
def generate_pdf(request):
    if request.user.is_superuser:
        if request.method == "POST":
            html_content = request.POST.get("html_content")

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = (
                'attachment; filename="techify_sales_report.pdf"'
            )
            pisa_status = pisa.CreatePDF(html_content, dest=response)
            if pisa_status.err:
                return HttpResponse("PDF generation error")
            return response

        return HttpResponse("Wrong method recieved")
    return redirect("home:home_page")


# Download sales_report (Excel format)
@login_required(login_url="authentication:signin")
def generate_excel(request):
    if request.user.is_superuser:
        if request.method == "POST":
            html_content = request.POST.get("html_content")

            tables = pd.read_html(html_content)
            if not tables:
                return HttpResponse("No tables found in HTML content.")

            df = tables[0]
            output = BytesIO()

            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False)

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = (
                'attachment; filename="techify_sales_report.xlsx"'
            )

            output.seek(0)
            response.write(output.getvalue())
            return response

        return HttpResponse("Wrong method recieved")
    return redirect("home:home_page")


# Offer Management
@login_required(login_url="authentication:signin")
def offer_management(request):
    if request.user.is_superuser:
        offers = Offer.objects.all().order_by("-id")
        return render(request, "custom_admin/offer.html", {"offers": offers})
    return redirect("home:home_page")
