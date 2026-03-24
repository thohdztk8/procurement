from django.urls import path
from . import views

urlpatterns = [
    path("po-status/", views.POStatusReportView.as_view()),
    path("supplier-performance/", views.SupplierPerformanceReportView.as_view()),
    path("spend-by-category/", views.SpendByCategoryReportView.as_view()),
    path("accounts-payable/", views.AccountsPayableReportView.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
    path("export/po/", views.ExportPOReportView.as_view()),
]
