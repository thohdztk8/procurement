from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView

urlpatterns = [
    path("admin/", admin.site.urls),
    # API schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerUIView.as_view(url_name="schema"), name="swagger-ui"),
    # App APIs
    path("api/auth/", include("apps.authentication.urls")),
    path("api/master/", include("apps.master_data.urls")),
    path("api/requisitions/", include("apps.requisition.urls")),
    path("api/carts/", include("apps.cart.urls")),
    path("api/quotations/", include("apps.quotation.urls")),
    path("api/ipos/", include("apps.ipo.urls")),
    path("api/warehouse/", include("apps.warehouse.urls")),
    path("api/finance/", include("apps.finance.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/reports/", include("apps.reports.urls")),
    # Supplier public portal (token-based, no auth)
    path("portal/", include("apps.quotation.portal_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
