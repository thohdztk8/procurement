"""Public supplier portal — no authentication required."""
from django.urls import path
from .portal_views import SupplierQuotationPortalView, SupplierQuotationSubmitView

urlpatterns = [
    path("quotation/<str:token>/", SupplierQuotationPortalView.as_view(), name="supplier-portal"),
    path("quotation/<str:token>/submit/", SupplierQuotationSubmitView.as_view(), name="supplier-submit"),
]
