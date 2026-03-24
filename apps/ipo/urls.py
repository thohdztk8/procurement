from django.urls import path
from . import views

urlpatterns = [
    path("", views.IPOListView.as_view()),
    path("create/", views.CreateIPOView.as_view()),
    path("<int:pk>/", views.IPODetailView.as_view()),
    path("<int:pk>/submit/", views.SubmitIPOView.as_view()),
    path("<int:pk>/approve/", views.ApproveIPOView.as_view()),
    path("<int:pk>/reject/", views.RejectIPOView.as_view()),
    path("<int:pk>/confirm-in-progress/", views.ConfirmIPOInProgressView.as_view()),
]
