"""
URL configuration for techify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin-panel Url
    path("django-admin/", admin.site.urls),
    # Custom admin-panel Url
    path("admin/", include("admin_techify.urls")),
    # Custom Apps Urls
    path("", include("home.urls")),
    path("category/", include("category.urls")),
    path("brand/", include("brand.urls")),
    path("product/", include("product.urls")),
    path("offer/", include("offer.urls")),
    path("authentication/", include("authentication.urls")),
    path("cart/", include("cart.urls")),
    path("account/", include("account.urls")),
    path("wishlist/", include("wishlist.urls")),
    path("coupon/", include("coupon.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
