from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GoodsReceipt, GoodsReceiptLine
from .serializers import GoodsReceiptSerializer, DepartmentConfirmationSerializer
from .services import WarehouseService
from apps.authentication.permissions import IsWarehouseKeeper, IsDeptHead


class GoodsReceiptListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsWarehouseKeeper]
    serializer_class = GoodsReceiptSerializer
    filterset_fields = ["status", "order"]

    def get_queryset(self):
        return GoodsReceipt.objects.select_related("order", "received_by").prefetch_related("lines")

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)


class GoodsReceiptDetailView(generics.RetrieveAPIView):
    permission_classes = [IsWarehouseKeeper]
    serializer_class = GoodsReceiptSerializer
    queryset = GoodsReceipt.objects.prefetch_related("lines")


class ConfirmReceiptView(APIView):
    permission_classes = [IsDeptHead]

    def post(self, request, line_pk):
        line = GoodsReceiptLine.objects.select_related("receipt__order", "pr").get(pk=line_pk)
        quality_note = request.data.get("quality_note", "")
        WarehouseService.confirm_receipt(line, request.user, quality_note)
        return Response({"detail": "Đã xác nhận nhận hàng."})
