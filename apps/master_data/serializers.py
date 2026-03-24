from rest_framework import serializers
from .models import ItemCategory, Item, Supplier, SupplierContact


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.category_name", read_only=True)

    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "created_by"]

    def validate_item_code(self, value):
        qs = Item.objects.filter(item_code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Mã vật tư đã tồn tại.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class SupplierContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierContact
        fields = "__all__"
        read_only_fields = ["created_at"]


class SupplierSerializer(serializers.ModelSerializer):
    contacts = SupplierContactSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "created_by"]

    def validate_tax_code(self, value):
        if not value:
            return value
        qs = Supplier.objects.filter(tax_code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Mã số thuế đã tồn tại — có thể là NCC trùng. Vui lòng kiểm tra lại."
            )
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["created_by"] = request.user
        return super().create(validated_data)
