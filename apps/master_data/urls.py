from django.urls import path
from . import views

urlpatterns = [
    path("item-categories/", views.ItemCategoryListCreateView.as_view()),
    path("item-categories/<int:pk>/", views.ItemCategoryDetailView.as_view()),
    path("items/", views.ItemListCreateView.as_view()),
    path("items/<int:pk>/", views.ItemDetailView.as_view()),
    path("suppliers/", views.SupplierListCreateView.as_view()),
    path("suppliers/<int:pk>/", views.SupplierDetailView.as_view()),
    path("suppliers/<int:supplier_pk>/contacts/", views.SupplierContactListCreateView.as_view()),
    path("suppliers/<int:supplier_pk>/contacts/<int:pk>/", views.SupplierContactDetailView.as_view()),
]
