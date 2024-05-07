import calendar
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from xhtml2pdf import pisa

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.utils import timezone
from django.http import HttpResponse
from django.core.paginator import Paginator

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
            status="Delivered", delivered_date=current_date
        )
        daily_revenue = sum(order.total for order in daily_orders)
        # Total Sales
        total_sales = Orders.objects.filter(status="Delivered").count()
        # Top Selling Products
        top_selling_products = Product.objects.annotate(
            total_orders=Count("orders")
        ).order_by("-total_orders")[:7]
        # Top Selling Brands
        top_selling_brands = (
            Product.objects.values("brand__name")
            .annotate(total_quantity=Sum("orders__product_qty"))
            .order_by("-total_quantity")[:7]
        )
        top_brand_names = [brand["brand__name"] for brand in top_selling_brands]
        # Payment Methods Counts (for graph)
        payment_method_counts = (
            Orders.objects.filter(status="Delivered")
            .values("payment_method")
            .annotate(count=Count("payment_method"))
        )
        counts = [method_count["count"] for method_count in payment_method_counts]
        # Total Amt of each payment method
        payment_methods = ["Online Payment", "Cash on Delivery", "Wallet Payment"]
        methods_and_totals = {}
        for method in payment_methods:
            total_amount = (
                Orders.objects.filter(payment_method=method, status="Delivered")
                .annotate(
                    order_total=Sum(
                        F("product_price") * F("product_qty") - F("discount_amt")
                    )
                )
                .aggregate(total_amount=Sum("order_total"))["total_amount"]
                or 0
            )
            methods_and_totals[method] = total_amount
        # Sales graph data
        scrollTo = None
        label = []
        sales_count = []
        if request.method == "POST":
            time_frame = request.POST.get("time_frame")
            scrollTo = request.POST.get("scrollTo", None)

            if time_frame == "weekly":
                weekly_sales = (
                    Orders.objects.filter(status="Delivered")
                    .annotate(week=ExtractWeek("ordered_date"))
                    .values("week")
                    .annotate(total_sales=Count("id"))
                )
                for item in reversed(weekly_sales):
                    label.append("Week " + str(item["week"]))
                    sales_count.append(item["total_sales"])
            elif time_frame == "monthly":
                monthly_sales = (
                    Orders.objects.filter(status="Delivered")
                    .annotate(month=ExtractMonth("ordered_date"))
                    .values("month")
                    .annotate(total_sales=Count("id"))
                )
                for item in reversed(monthly_sales):
                    label.append(calendar.month_name[item["month"]])
                    sales_count.append(item["total_sales"])
            elif time_frame == "yearly":
                yearly_sales = (
                    Orders.objects.filter(status="Delivered")
                    .annotate(year=ExtractYear("ordered_date"))
                    .values("year")
                    .annotate(total_sales=Count("id"))
                )
                for item in reversed(yearly_sales):
                    label.append(item["year"])
                    sales_count.append(item["total_sales"])
        else:
            monthly_sales = (
                Orders.objects.filter(status="Delivered")
                .annotate(month=ExtractMonth("ordered_date"))
                .values("month")
                .annotate(total_sales=Count("id"))
            )
            for item in reversed(monthly_sales):
                label.append(calendar.month_name[item["month"]])
                sales_count.append(item["total_sales"])

        context = {
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "daily_revenue": daily_revenue,
            "total_sales": total_sales,
            "top_products": top_selling_products,
            "top_brands": top_brand_names,
            "counts": counts,
            "methods_and_totals": methods_and_totals,
            "scrollTo": scrollTo,
            "label": label,
            "sales_count": sales_count,
        }
        return render(request, "custom_admin/index.html", context)
    return redirect("home:home_page")


# User Management
@login_required(login_url="authentication:signin")
def user_management(request):
    if request.user.is_superuser:
        users = User.objects.exclude(is_superuser=True).order_by("-id")
        paginator = Paginator(users, 10)
        page_number = request.GET.get("page")
        user_obj = paginator.get_page(page_number)
        return render(request, "custom_admin/user.html", {"user_obj": user_obj})
    return redirect("home:home_page")


# Brand Management
@login_required(login_url="authentication:signin")
def brand_management(request):
    if request.user.is_superuser:
        brands = Brand.objects.annotate(products_count=Count("product")).order_by("-id")
        paginator = Paginator(brands, 10)
        page_number = request.GET.get("page")
        brand_obj = paginator.get_page(page_number)
        return render(request, "custom_admin/brand.html", {"brand_obj": brand_obj})
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
        paginator = Paginator(categories, 10)
        page_number = request.GET.get("page")
        category_obj = paginator.get_page(page_number)
        # offer alert message
        if "message" in request.session:
            message = request.session.pop("message")
        else:
            message = None
        context = {"category_obj": category_obj, "offers": offers, "message": message}
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
        paginator = Paginator(products, 10)
        page_number = request.GET.get("page")
        product_obj = paginator.get_page(page_number)
        context = {"product_obj": product_obj, "offers": offers}
        return render(request, "custom_admin/product.html", context)
    return redirect("home:home_page")


# Order Management
@login_required(login_url="authentication:signin")
def order_management(request):
    if request.user.is_superuser:
        orders = Orders.objects.all().order_by("-id")
        paginator = Paginator(orders, 10)
        page_number = request.GET.get("page")
        order_obj = paginator.get_page(page_number)
        return render(request, "custom_admin/orders.html", {"order_obj": order_obj})
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
        paginator = Paginator(coupons, 10)
        page_number = request.GET.get("page")
        coupon_obj = paginator.get_page(page_number)
        return render(request, "custom_admin/coupon.html", {"coupon_obj": coupon_obj})
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
        paginator = Paginator(offers, 10)
        page_number = request.GET.get("page")
        offer_obj = paginator.get_page(page_number)
        return render(request, "custom_admin/offer.html", {"offer_obj": offer_obj})
    return redirect("home:home_page")
