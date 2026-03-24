from rest_framework import serializers
from .models import Invoice, PaymentRequest, Payment, CreditNote


class InvoiceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.company_name", read_only=True)
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ["uploaded_by", "uploaded_at", "status"]

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)


class PaymentRequestSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    ipo_number = serializers.CharField(source="ipo.ipo_number", read_only=True)

    class Meta:
        model = PaymentRequest
        fields = "__all__"
        read_only_fields = ["request_number", "requested_by", "created_at", "updated_at"]

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        ipo = attrs.get("ipo")
        if invoice and invoice.status not in [Invoice.STATUS_PENDING]:
            raise serializers.ValidationError("Hóa đơn không ở trạng thái hợp lệ để tạo yêu cầu TT.")
        if ipo and ipo.status not in ["approved", "in_progress", "completed"]:
            raise serializers.ValidationError("IPO chưa được phê duyệt.")
        return attrs

    def create(self, validated_data):
        validated_data["requested_by"] = self.context["request"].user
        pr = super().create(validated_data)
        pr.invoice.status = Invoice.STATUS_PAYMENT_REQUESTED
        pr.invoice.save(update_fields=["status"])
        from apps.notifications.services import NotificationService
        NotificationService.notify_payment_request(pr)
        return pr


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["paid_by", "paid_at"]

    def create(self, validated_data):
        validated_data["paid_by"] = self.context["request"].user
        payment = super().create(validated_data)
        pr = payment.payment_request
        pr.status = PaymentRequest.STATUS_PAID
        pr.save(update_fields=["status", "updated_at"])
        pr.invoice.status = Invoice.STATUS_PAID
        pr.invoice.save(update_fields=["status"])
        return payment


class CreditNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        cn = super().create(validated_data)
        cn.invoice.status = Invoice.STATUS_CREDIT_NOTED
        cn.invoice.save(update_fields=["status"])
        return cn
