"""
Module: Purchase Requisition (PR)
Tables: PurchaseRequisition, PRHistory
"""
from django.db import models
from apps.authentication.models import User, Department
from apps.master_data.models import Item


class PurchaseRequisition(models.Model):
    STATUS_PENDING = "pending"
    STATUS_IN_CART = "in_cart"
    STATUS_PROCESSING = "processing"
    STATUS_RECEIVED = "received"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ xử lý"),
        (STATUS_IN_CART, "Đã vào cart"),
        (STATUS_PROCESSING, "Đang xử lý"),
        (STATUS_RECEIVED, "Đã nhận hàng"),
        (STATUS_CANCELLED, "Đã hủy"),
    ]

    PRIORITY_NORMAL = "normal"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_NORMAL, "Thường"),
        (PRIORITY_URGENT, "Khẩn"),
    ]

    pr_number = models.CharField(max_length=30, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="requisitions")
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="requisitions")
    item = models.ForeignKey(
        Item, on_delete=models.SET_NULL, null=True, blank=True, related_name="requisitions"
    )
    item_name_free_text = models.CharField(max_length=250, null=True, blank=True)
    is_other_item = models.BooleanField(default=False)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    unit_of_measure = models.CharField(max_length=50)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)
    required_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cancel_reason = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PurchaseRequisition"
        ordering = ["-created_at"]

    def __str__(self):
        return self.pr_number

    def get_item_name(self):
        if self.is_other_item:
            return self.item_name_free_text
        return self.item.item_name if self.item else ""

    def save(self, *args, **kwargs):
        if not self.pr_number:
            from django.utils import timezone
            year = timezone.now().year
            count = PurchaseRequisition.objects.filter(
                created_at__year=year
            ).count() + 1
            self.pr_number = f"PR-{year}-{count:05d}"
        super().save(*args, **kwargs)


class PRHistory(models.Model):
    CHANGE_CREATED = "created"
    CHANGE_UPDATED = "updated"
    CHANGE_CANCELLED = "cancelled"
    CHANGE_STATUS = "status_changed"

    pr = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="history")
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    change_type = models.CharField(max_length=50)
    field_changed = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    note = models.CharField(max_length=500, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PRHistory"
        ordering = ["-changed_at"]
