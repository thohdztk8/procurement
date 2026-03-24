from rest_framework import serializers
from django.utils import timezone
from .models import QuotationSession, QuotationLine, QuotationSubmitHistory


class QuotationLineSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="order_line.item_name_display", read_only=True)
    quantity = serializers.DecimalField(source="order_line.total_quantity", max_digits=18, decimal_places=4, read_only=True)
    uom = serializers.CharField(source="order_line.unit_of_measure", read_only=True)

    class Meta:
        model = QuotationLine
        fields = "__all__"
        read_only_fields = ["session", "order_line", "submitted_at", "is_selected"]


class QuotationSessionSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="order_supplier.supplier.company_name", read_only=True)
    lines = QuotationLineSerializer(many=True, read_only=True)
    portal_url = serializers.SerializerMethodField()

    class Meta:
        model = QuotationSession
        fields = "__all__"
        read_only_fields = ["quotation_token", "email_sent_at", "email_sent_by", "created_at"]

    def get_portal_url(self, obj):
        return obj.get_portal_url()


class SendQuotationSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    supplier_ids = serializers.ListField(child=serializers.IntegerField())
    expiry_hours = serializers.IntegerField(default=72)


class SupplierQuotationSubmitSerializer(serializers.Serializer):
    """Used by supplier portal — no auth required."""
    lines = serializers.ListField(child=serializers.DictField())

    def validate_lines(self, value):
        for line in value:
            if "quotation_line_id" not in line or "unit_price" not in line:
                raise serializers.ValidationError(
                    "Mỗi dòng cần có quotation_line_id và unit_price."
                )
        return value


class SelectQuotationSerializer(serializers.Serializer):
    """Staff selects winning lines."""
    selected_line_ids = serializers.ListField(child=serializers.IntegerField())
