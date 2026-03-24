from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartListCreateView.as_view()),
    path("<int:pk>/", views.CartDetailView.as_view()),
    path("<int:pk>/add-pr/", views.AddPRToCartView.as_view()),
    path("<int:pk>/remove-pr/<int:pr_pk>/", views.RemovePRFromCartView.as_view()),
    path("orders/create/", views.CreateOrderView.as_view()),
    path("orders/", views.OrderListView.as_view()),
    path("orders/<int:pk>/", views.OrderDetailView.as_view()),
    path("orders/<int:pk>/update-status/", views.UpdateOrderStatusView.as_view()),
]
