from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import QuotationSession, QuotationLine
from .serializers import (
    QuotationSessionSerializer, SendQuotationSerializer,
    SupplierQuotationSubmitSerializer, SelectQuotationSerializer,
)
from .services import QuotationService
from apps.authentication.permissions import IsAdminOrPurchasing
from apps.cart.models import PurchaseOrder


class SendQuotationView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request):
        serializer = SendQuotationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = PurchaseOrder.objects.get(pk=serializer.validated_data["order_id"])
        sessions = QuotationService.send_quotation_requests(
            order,
            serializer.validated_data["supplier_ids"],
            request.user,
            serializer.validated_data.get("expiry_hours", 72),
        )
        return Response({
            "detail": f"Đã gửi yêu cầu báo giá đến {len(sessions)} nhà cung cấp.",
            "sessions": [{"id": s.pk, "portal_url": s.get_portal_url()} for s in sessions],
        })


class QuotationSessionListView(generics.ListAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = QuotationSessionSerializer

    def get_queryset(self):
        return QuotationSession.objects.select_related(
            "order_supplier__supplier", "order"
        ).prefetch_related("lines__order_line")


class QuotationSessionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = QuotationSessionSerializer
    queryset = QuotationSession.objects.prefetch_related("lines__order_line")


class SelectQuotationView(APIView):
    """Staff selects winning quotation lines and creates IPO draft."""
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request, pk):
        order = PurchaseOrder.objects.get(pk=pk)
        serializer = SelectQuotationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected_ids = serializer.validated_data["selected_line_ids"]
        QuotationLine.objects.filter(pk__in=selected_ids).update(is_selected=True)
        order.status = PurchaseOrder.STATUS_IPO_DRAFT
        order.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Đã chốt báo giá. Có thể xuất IPO."})


class SupplierQuotationPortalView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        """Supplier truy cập portal báo giá qua token"""
        try:
            session = QuotationSession.objects.get(quotation_token=token)
        except QuotationSession.DoesNotExist:
            return Response({"detail": "Token không hợp lệ hoặc đã hết hạn."}, status=404)
        if session.token_expiry < timezone.now():
            return Response({"detail": "Token đã hết hạn."}, status=410)
        data = QuotationSessionSerializer(session).data
        return Response(data)

    def post(self, request, token):
        """Supplier submit báo giá qua token"""
        try:
            session = QuotationSession.objects.get(quotation_token=token)
        except QuotationSession.DoesNotExist:
            return Response({"detail": "Token không hợp lệ hoặc đã hết hạn."}, status=404)
        if session.token_expiry < timezone.now():
            return Response({"detail": "Token đã hết hạn."}, status=410)
        if session.status != QuotationSession.STATUS_PENDING:
            return Response({"detail": "Phiên báo giá đã đóng hoặc đã submit."}, status=400)
        serializer = SupplierQuotationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for line in serializer.validated_data["lines"]:
            try:
                ql = QuotationLine.objects.get(pk=line["quotation_line_id"], session=session)
                ql.unit_price = line["unit_price"]
                ql.save(update_fields=["unit_price"])
            except QuotationLine.DoesNotExist:
                continue
        session.status = QuotationSession.STATUS_SUBMITTED
        session.save(update_fields=["status"])
        return Response({"detail": "Đã submit báo giá thành công."})
