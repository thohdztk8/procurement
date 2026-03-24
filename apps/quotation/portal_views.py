"""Supplier portal views — token-based, no auth required."""
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import QuotationSession
from .serializers import QuotationSessionSerializer, SupplierQuotationSubmitSerializer
from .services import QuotationService


class SupplierQuotationPortalView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            session = QuotationSession.objects.select_related(
                "order_supplier__supplier", "order"
            ).prefetch_related("lines__order_line").get(quotation_token=token)
        except QuotationSession.DoesNotExist:
            return Response({"detail": "Link không hợp lệ."}, status=status.HTTP_404_NOT_FOUND)
        if timezone.now() > session.token_expiry:
            return Response(
                {"detail": "Link báo giá đã hết hạn.", "expired": True},
                status=status.HTTP_410_GONE
            )
        return Response({
            "session": QuotationSessionSerializer(session).data,
            "supplier_name": session.order_supplier.supplier.company_name,
            "order_number": session.order.order_number,
            "deadline": session.token_expiry,
        })


class SupplierQuotationSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            session = QuotationSession.objects.get(quotation_token=token)
        except QuotationSession.DoesNotExist:
            return Response({"detail": "Link không hợp lệ."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierQuotationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = request.META.get("REMOTE_ADDR", "")
        try:
            QuotationService.submit_quotation(session, serializer.validated_data["lines"], ip)
            return Response({"detail": "Báo giá đã được gửi thành công. Cảm ơn bạn!"})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
