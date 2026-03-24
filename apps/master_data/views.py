from rest_framework import generics, status
from rest_framework.response import Response
from .models import ItemCategory, Item, Supplier, SupplierContact
from .serializers import (
    ItemCategorySerializer, ItemSerializer,
    SupplierSerializer, SupplierContactSerializer,
)
from apps.authentication.permissions import IsAdminOrPurchasing


class ItemCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    filterset_fields = ["is_active"]
    search_fields = ["category_code", "category_name"]


class ItemCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrPurchasing]
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer


class ItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    queryset = Item.objects.select_related("category", "created_by").filter(is_active=True)
    serializer_class = ItemSerializer
    filterset_fields = ["category", "is_active"]
    search_fields = ["item_code", "item_name"]
    ordering_fields = ["item_code", "item_name", "created_at"]


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrPurchasing]
    queryset = Item.objects.select_related("category").all()
    serializer_class = ItemSerializer

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.is_active = False
        item.save(update_fields=["is_active"])
        return Response({"detail": "Vật tư đã bị ngừng sử dụng."}, status=status.HTTP_200_OK)


class SupplierListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    queryset = Supplier.objects.prefetch_related("contacts").all()
    serializer_class = SupplierSerializer
    filterset_fields = ["status"]
    search_fields = ["supplier_code", "company_name", "tax_code"]


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrPurchasing]
    queryset = Supplier.objects.prefetch_related("contacts").all()
    serializer_class = SupplierSerializer

    def destroy(self, request, *args, **kwargs):
        supplier = self.get_object()
        supplier.status = Supplier.STATUS_SUSPENDED
        supplier.save(update_fields=["status"])
        return Response({"detail": "NCC đã bị tạm dừng."}, status=status.HTTP_200_OK)


class SupplierContactListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = SupplierContactSerializer

    def get_queryset(self):
        return SupplierContact.objects.filter(supplier_id=self.kwargs["supplier_pk"])

    def perform_create(self, serializer):
        serializer.save(supplier_id=self.kwargs["supplier_pk"])


class SupplierContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrPurchasing]
    serializer_class = SupplierContactSerializer

    def get_queryset(self):
        return SupplierContact.objects.filter(supplier_id=self.kwargs["supplier_pk"])
