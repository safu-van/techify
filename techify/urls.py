from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin-panel Url
    path("django-admin/", admin.site.urls),

    # Custom admin-panel Url
    path("techify-admin/", include("admin_techify.urls")),
    
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
