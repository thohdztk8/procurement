from rest_framework import serializers
from .models import PurchaseRequisition, PRHistory


class PRHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)

    class Meta:
        model = PRHistory
        fields = "__all__"


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source="department.department_name", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.full_name", read_only=True)
    history = PRHistorySerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = "__all__"
        read_only_fields = ["pr_number", "status", "created_at", "updated_at",
                            "department", "requested_by"]

    def get_item_name(self, obj):
        return obj.get_item_name()

    def validate(self, attrs):
        if attrs.get("is_other_item") and not attrs.get("item_name_free_text"):
            raise serializers.ValidationError(
                {"item_name_free_text": "Bắt buộc nhập tên vật tư khi chọn loại Other."}
            )
        if not attrs.get("is_other_item") and not attrs.get("item"):
            raise serializers.ValidationError(
                {"item": "Vui lòng chọn vật tư từ danh mục hoặc chọn loại Other."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["requested_by"] = request.user
        validated_data["department"] = request.user.department
        if validated_data.get("item") and not validated_data.get("unit_of_measure"):
            validated_data["unit_of_measure"] = validated_data["item"].unit_of_measure
        pr = super().create(validated_data)
        PRHistory.objects.create(
            pr=pr, changed_by=request.user, change_type="created",
            new_value=f"PR tạo bởi {request.user.full_name}"
        )
        return pr


class PRCancelSerializer(serializers.Serializer):
    cancel_reason = serializers.CharField(max_length=500)
