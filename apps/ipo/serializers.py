from rest_framework import serializers
from .models import IPO, IPOLine, IPOHistory


class IPOLineSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.company_name", read_only=True)

    class Meta:
        model = IPOLine
        fields = "__all__"


class IPOHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)

    class Meta:
        model = IPOHistory
        fields = "__all__"


class IPOSerializer(serializers.ModelSerializer):
    lines = IPOLineSerializer(many=True, read_only=True)
    history = IPOHistorySerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True)

    class Meta:
        model = IPO
        fields = "__all__"
        read_only_fields = ["ipo_number", "created_by", "created_at", "updated_at",
                            "submitted_at", "approved_at", "rejected_at"]


class CreateIPOSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    lines = serializers.ListField(child=serializers.DictField())
    notes = serializers.CharField(required=False, allow_blank=True)


class ApproveIPOSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class RejectIPOSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(max_length=1000)
