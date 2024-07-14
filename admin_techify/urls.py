from django.urls import path
from admin_techify import views

app_name = "admin_techify"


urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),

    path("category-management/", views.category_management, name="category_management"),

    path("brand-management/", views.brand_management, name="brand_management"),

    path("user-management/", views.user_management, name="user_management"),

    path("product-management/", views.product_management, name="product_management"),

    path("order-management/", views.order_management, name="order_management"),
    path("order-details/<int:order_id>/", views.order_details, name="order_details"),

    path("coupon-management/", views.coupon_management, name="coupon_management"),

    path("offer-management/", views.offer_management, name="offer_management"),
    
    path("sales-report/", views.sales_report, name="sales_report"),
    path("generate-pdf/", views.generate_pdf, name="generate_pdf"),
    path("generate-excel/", views.generate_excel, name="generate_excel"),
]
