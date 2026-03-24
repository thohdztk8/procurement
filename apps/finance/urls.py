from django.urls import path
from . import views

urlpatterns = [
    path("invoices/", views.InvoiceListCreateView.as_view()),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view()),
    path("payment-requests/", views.PaymentRequestListCreateView.as_view()),
    path("payment-requests/<int:pk>/", views.PaymentRequestDetailView.as_view()),
    path("payments/", views.PaymentListCreateView.as_view()),
    path("credit-notes/", views.CreditNoteListCreateView.as_view()),
]
