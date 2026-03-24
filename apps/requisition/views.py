from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import PurchaseRequisition, PRHistory
from .serializers import PurchaseRequisitionSerializer, PRCancelSerializer
from apps.authentication.permissions import IsDeptHead, IsAdminOrPurchasing
from apps.authentication.models import Role
from rest_framework.permissions import IsAuthenticated


class PurchaseRequisitionListCreateView(generics.ListCreateAPIView):
    serializer_class = PurchaseRequisitionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "department"]
    search_fields = ["pr_number", "item__item_name", "item_name_free_text"]
    ordering_fields = ["created_at", "priority", "required_date"]

    def get_queryset(self):
        user = self.request.user
        qs = PurchaseRequisition.objects.select_related(
            "item", "department", "requested_by"
        ).prefetch_related("history")
        # Dept heads see only their dept PRs
        if user.has_role(Role.DEPT_HEAD):
            return qs.filter(department=user.department)
        # Purchasing / admin see all
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsDeptHead()]
        return [IsAuthenticated()]


class PurchaseRequisitionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PurchaseRequisitionSerializer

    def get_queryset(self):
        return PurchaseRequisition.objects.select_related(
            "item", "department", "requested_by"
        ).prefetch_related("history")

    def update(self, request, *args, **kwargs):
        pr = self.get_object()
        if pr.status not in [PurchaseRequisition.STATUS_PENDING]:
            return Response(
                {"detail": "Chỉ có thể chỉnh sửa PR ở trạng thái Chờ xử lý."},
                status=status.HTTP_400_BAD_REQUEST
            )
        response = super().update(request, *args, **kwargs)
        PRHistory.objects.create(
            pr=pr, changed_by=request.user, change_type="updated",
            note="Cập nhật thông tin PR"
        )
        return response


class CancelPRView(APIView):
    def post(self, request, pk):
        pr = PurchaseRequisition.objects.get(pk=pk)
        if pr.status in [PurchaseRequisition.STATUS_RECEIVED, PurchaseRequisition.STATUS_CANCELLED]:
            return Response(
                {"detail": "Không thể hủy PR ở trạng thái này."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PRCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pr.status = PurchaseRequisition.STATUS_CANCELLED
        pr.cancel_reason = serializer.validated_data["cancel_reason"]
        pr.save()
        PRHistory.objects.create(
            pr=pr, changed_by=request.user, change_type="cancelled",
            new_value=pr.cancel_reason
        )
        from apps.notifications.services import NotificationService
        NotificationService.notify_pr_cancelled(pr)
        return Response({"detail": "PR đã được hủy."})
