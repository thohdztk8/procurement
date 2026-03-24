from django.urls import path
from . import views

urlpatterns = [
    path("receipts/", views.GoodsReceiptListCreateView.as_view()),
    path("receipts/<int:pk>/", views.GoodsReceiptDetailView.as_view()),
    path("receipt-lines/<int:line_pk>/confirm/", views.ConfirmReceiptView.as_view()),
]
