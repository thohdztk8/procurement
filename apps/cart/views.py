from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem, PurchaseOrder, OrderStatusHistory
from .serializers import (
    CartSerializer, AddPRToCartSerializer,
    PurchaseOrderSerializer, CreateOrderFromCartSerializer, UpdateOrderStatusSerializer,
)
from .services import CartService, OrderService
from apps.authentication.permissions import IsAdminOrPurchasing
from apps.requisition.models import PurchaseRequisition


class CartListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.prefetch_related("items__pr").filter(
            created_by=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CartDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.prefetch_related("items__pr")


class AddPRToCartView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request, pk):
        cart = Cart.objects.get(pk=pk)
        serializer = AddPRToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pr = PurchaseRequisition.objects.get(pk=serializer.validated_data["pr_id"])
        try:
            item = CartService.add_pr_to_cart(
                cart, pr, request.user,
                serializer.validated_data.get("quantity_override"),
                serializer.validated_data.get("item_name_override"),
            )
            return Response({"detail": "PR đã được thêm vào cart.", "cart_item_id": item.pk})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RemovePRFromCartView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request, pk, pr_pk):
        cart = Cart.objects.get(pk=pk)
        pr = PurchaseRequisition.objects.get(pk=pr_pk)
        try:
            CartService.remove_pr_from_cart(cart, pr, request.user)
            return Response({"detail": "PR đã được gỡ khỏi cart."})
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateOrderView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request):
        serializer = CreateOrderFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = Cart.objects.get(pk=serializer.validated_data["cart_id"])
        try:
            order = OrderService.create_order_from_cart(
                cart,
                serializer.validated_data["supplier_ids"],
                request.user,
                serializer.validated_data.get("notes", ""),
            )
            return Response(PurchaseOrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except (ValueError, Exception) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ["status"]
    search_fields = ["order_number"]

    def get_queryset(self):
        return PurchaseOrder.objects.select_related("created_by", "cart").prefetch_related(
            "lines", "suppliers__supplier", "status_history"
        )


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = PurchaseOrderSerializer
    queryset = PurchaseOrder.objects.prefetch_related("lines", "suppliers__supplier", "status_history")


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminOrPurchasing]

    def post(self, request, pk):
        order = PurchaseOrder.objects.get(pk=pk)
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_status = order.status
        order.status = serializer.validated_data["status"]
        order.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(
            order=order, old_status=old_status,
            new_status=order.status,
            changed_by=request.user,
            note=serializer.validated_data.get("note", ""),
        )
        return Response({"detail": "Trạng thái đơn hàng đã được cập nhật."})
