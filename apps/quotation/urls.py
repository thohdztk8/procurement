from django.urls import path
from . import views

urlpatterns = [
    path("send/", views.SendQuotationView.as_view()),
    path("sessions/", views.QuotationSessionListView.as_view()),
    path("sessions/<int:pk>/", views.QuotationSessionDetailView.as_view()),
    path("orders/<int:pk>/select/", views.SelectQuotationView.as_view()),
    path("portal/<str:token>/", views.SupplierQuotationPortalView.as_view()),
]
