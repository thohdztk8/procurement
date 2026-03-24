from rest_framework import serializers
from .models import GoodsReceipt, GoodsReceiptLine, DepartmentConfirmation


class GoodsReceiptLineSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="order_line.item_name_display", read_only=True)
    quantity_diff = serializers.DecimalField(max_digits=18, decimal_places=4, read_only=True)

    class Meta:
        model = GoodsReceiptLine
        fields = "__all__"


class GoodsReceiptSerializer(serializers.ModelSerializer):
    lines = GoodsReceiptLineSerializer(many=True)
    received_by_name = serializers.CharField(source="received_by.full_name", read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = "__all__"
        read_only_fields = ["receipt_number", "received_by", "created_at"]

    def create(self, validated_data):
        lines_data = validated_data.pop("lines")
        receipt = GoodsReceipt.objects.create(**validated_data)
        for ld in lines_data:
            GoodsReceiptLine.objects.create(receipt=receipt, **ld)
        return receipt


class DepartmentConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentConfirmation
        fields = "__all__"
        read_only_fields = ["confirmed_by", "confirmed_at"]
