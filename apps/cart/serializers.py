from rest_framework import serializers
from .models import Cart, CartItem, PurchaseOrder, OrderLine, OrderSupplier, OrderStatusHistory
from apps.requisition.serializers import PurchaseRequisitionSerializer


class CartItemSerializer(serializers.ModelSerializer):
    pr_number = serializers.CharField(source="pr.pr_number", read_only=True)
    item_name = serializers.SerializerMethodField()
    effective_quantity = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ["added_by", "added_at"]

    def get_item_name(self, obj):
        return obj.effective_item_name()

    def get_effective_quantity(self, obj):
        return obj.effective_quantity()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at", "status"]


class AddPRToCartSerializer(serializers.Serializer):
    pr_id = serializers.IntegerField()
    quantity_override = serializers.DecimalField(max_digits=18, decimal_places=4, required=False)
    item_name_override = serializers.CharField(max_length=250, required=False)


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = "__all__"


class OrderSupplierSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.company_name", read_only=True)

    class Meta:
        model = OrderSupplier
        fields = "__all__"
        read_only_fields = ["added_by", "added_at"]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = "__all__"


class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, read_only=True)
    suppliers = OrderSupplierSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = ["order_number", "created_by", "created_at", "updated_at"]


class CreateOrderFromCartSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    supplier_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    notes = serializers.CharField(required=False, allow_blank=True)


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=PurchaseOrder.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)
