from rest_framework import generics
from .models import Invoice, PaymentRequest, Payment, CreditNote
from .serializers import InvoiceSerializer, PaymentRequestSerializer, PaymentSerializer, CreditNoteSerializer
from apps.authentication.permissions import IsAdminOrPurchasing, IsAccountant


class InvoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = InvoiceSerializer
    filterset_fields = ["status", "supplier", "order"]
    search_fields = ["invoice_number"]

    def get_queryset(self):
        return Invoice.objects.select_related("supplier", "order", "uploaded_by")


class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()


class PaymentRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentRequestSerializer
    filterset_fields = ["status"]

    def get_queryset(self):
        return PaymentRequest.objects.select_related("invoice", "ipo", "requested_by")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrPurchasing()]
        return [IsAccountant()]


class PaymentRequestDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentRequestSerializer
    queryset = PaymentRequest.objects.all()


class PaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAccountant]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related("payment_request", "paid_by")


class CreditNoteListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAccountant]
    serializer_class = CreditNoteSerializer

    def get_queryset(self):
        return CreditNote.objects.select_related("invoice", "supplier", "created_by")
