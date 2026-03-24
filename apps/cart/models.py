"""
Module: Cart & Order
Tables: Cart, CartItem, CartHistory, PurchaseOrder, OrderLine, OrderLinePR,
        OrderSupplier, OrderStatusHistory
"""
from django.db import models
from apps.authentication.models import User
from apps.master_data.models import Item, Supplier
from apps.requisition.models import PurchaseRequisition


class Cart(models.Model):
    STATUS_OPEN = "open"
    STATUS_CONVERTED = "converted"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Đang mở"),
        (STATUS_CONVERTED, "Đã tạo order"),
        (STATUS_CLOSED, "Đã đóng"),
    ]

    cart_title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="carts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    notes = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Cart"
        ordering = ["-created_at"]

    def __str__(self):
        return self.cart_title


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    pr = models.ForeignKey(PurchaseRequisition, on_delete=models.PROTECT, related_name="cart_items")
    quantity_override = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    item_name_override = models.CharField(max_length=250, null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="added_cart_items")
    added_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="removed_cart_items"
    )

    class Meta:
        db_table = "CartItem"

    def effective_quantity(self):
        return self.quantity_override if self.quantity_override else self.pr.quantity

    def effective_item_name(self):
        return self.item_name_override if self.item_name_override else self.pr.get_item_name()


class CartHistory(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="history")
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    change_type = models.CharField(max_length=50)  # item_added | item_removed | item_modified
    pr = models.ForeignKey(
        PurchaseRequisition, on_delete=models.SET_NULL, null=True, blank=True
    )
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CartHistory"


class PurchaseOrder(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_QUOTATION_SENT = "quotation_sent"
    STATUS_QUOTATION_RECEIVED = "quotation_received"
    STATUS_IPO_DRAFT = "ipo_draft"
    STATUS_IPO_PENDING = "ipo_pending"
    STATUS_IPO_APPROVED = "ipo_approved"
    STATUS_IPO_REJECTED = "ipo_rejected"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DELIVERED = "delivered"
    STATUS_PARTIAL = "partial_delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Nháp"),
        (STATUS_QUOTATION_SENT, "Đã gửi báo giá"),
        (STATUS_QUOTATION_RECEIVED, "Đã nhận báo giá"),
        (STATUS_IPO_DRAFT, "IPO nháp"),
        (STATUS_IPO_PENDING, "IPO chờ duyệt"),
        (STATUS_IPO_APPROVED, "IPO đã duyệt"),
        (STATUS_IPO_REJECTED, "IPO từ chối"),
        (STATUS_IN_PROGRESS, "Đang thực hiện"),
        (STATUS_DELIVERED, "Đã giao"),
        (STATUS_PARTIAL, "Giao một phần"),
        (STATUS_CANCELLED, "Đã hủy"),
    ]

    order_number = models.CharField(max_length=30, unique=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, related_name="orders")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PurchaseOrder"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.utils import timezone
            year = timezone.now().year
            count = PurchaseOrder.objects.filter(created_at__year=year).count() + 1
            self.order_number = f"PO-{year}-{count:05d}"
        super().save(*args, **kwargs)


class OrderLine(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    item_name_display = models.CharField(max_length=250)
    unit_of_measure = models.CharField(max_length=50)
    total_quantity = models.DecimalField(max_digits=18, decimal_places=4)
    notes = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "OrderLine"


class OrderLinePR(models.Model):
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name="pr_links")
    pr = models.ForeignKey(PurchaseRequisition, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta:
        db_table = "OrderLinePR"


class OrderSupplier(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="suppliers")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    contact_override_name = models.CharField(max_length=150, null=True, blank=True)
    contact_override_email = models.EmailField(max_length=200, null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.PROTECT)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "OrderSupplier"
        unique_together = [["order", "supplier"]]


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=30, null=True, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    note = models.CharField(max_length=500, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "OrderStatusHistory"
