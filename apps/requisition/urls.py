from django.urls import path
from . import views

urlpatterns = [
    path("", views.PurchaseRequisitionListCreateView.as_view(), name="pr-list"),
    path("<int:pk>/", views.PurchaseRequisitionDetailView.as_view(), name="pr-detail"),
    path("<int:pk>/cancel/", views.CancelPRView.as_view(), name="pr-cancel"),
]
