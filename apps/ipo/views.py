from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import IPO
from .serializers import IPOSerializer, CreateIPOSerializer, ApproveIPOSerializer, RejectIPOSerializer
from .services import IPOService
from apps.authentication.permissions import IsAdminOrPurchasing, IsApprover, IsPurchasingManager
from apps.cart.models import PurchaseOrder


class IPOListView(generics.ListAPIView):
    serializer_class = IPOSerializer
    filterset_fields = ["status"]
    search_fields = ["ipo_number"]

    def get_queryset(self):
        return IPO.objects.select_related("created_by", "approved_by").prefetch_related("lines__supplier", "history")


class IPODetailView(generics.RetrieveAPIView):
    serializer_class = IPOSerializer
    queryset = IPO.objects.prefetch_related("lines__supplier", "history")


class CreateIPOView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request):
        serializer = CreateIPOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = PurchaseOrder.objects.get(pk=serializer.validated_data["order_id"])
        ipo = IPOService.create_ipo(
            order, serializer.validated_data["lines"],
            request.user, serializer.validated_data.get("notes", "")
        )
        return Response(IPOSerializer(ipo).data, status=status.HTTP_201_CREATED)


class SubmitIPOView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request, pk):
        ipo = IPO.objects.get(pk=pk)
        try:
            IPOService.submit_for_approval(ipo, request.user)
            return Response({"detail": "IPO đã được gửi để phê duyệt."})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ApproveIPOView(APIView):
    permission_classes = [IsApprover]

    def post(self, request, pk):
        ipo = IPO.objects.get(pk=pk)
        serializer = ApproveIPOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            IPOService.approve(ipo, request.user, serializer.validated_data.get("notes", ""))
            return Response({"detail": "IPO đã được phê duyệt."})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RejectIPOView(APIView):
    permission_classes = [IsApprover]

    def post(self, request, pk):
        ipo = IPO.objects.get(pk=pk)
        serializer = RejectIPOSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            IPOService.reject(ipo, request.user, serializer.validated_data["rejection_reason"])
            return Response({"detail": "IPO đã bị từ chối."})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmIPOInProgressView(APIView):
    """Trưởng phòng MH xác nhận đã liên hệ NCC, chuyển sang đang thực hiện."""
    permission_classes = [IsPurchasingManager]

    def post(self, request, pk):
        ipo = IPO.objects.get(pk=pk)
        if ipo.status != IPO.STATUS_APPROVED:
            return Response({"detail": "IPO chưa được duyệt."}, status=status.HTTP_400_BAD_REQUEST)
        ipo.status = IPO.STATUS_IN_PROGRESS
        ipo.save(update_fields=["status", "updated_at"])
        IPOService.__class__  # just reference
        from .models import IPOHistory
        IPOHistory.objects.create(
            ipo=ipo, changed_by=request.user, change_type="status_changed",
            old_status=IPO.STATUS_APPROVED, new_status=IPO.STATUS_IN_PROGRESS,
            note="Trưởng phòng xác nhận đã liên hệ NCC"
        )
        ipo.order.status = PurchaseOrder.STATUS_IN_PROGRESS
        ipo.order.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Đã xác nhận đang thực hiện mua hàng."})
