"""
Module: Warehouse
Tables: GoodsReceipt, GoodsReceiptLine, DepartmentConfirmation
"""
from django.db import models
from apps.authentication.models import User
from apps.cart.models import PurchaseOrder, OrderLine
from apps.requisition.models import PurchaseRequisition


class GoodsReceipt(models.Model):
    STATUS_PARTIAL = "partial"
    STATUS_COMPLETE = "complete"
    STATUS_CHOICES = [
        (STATUS_PARTIAL, "Nhận một phần"),
        (STATUS_COMPLETE, "Nhận đủ"),
    ]

    receipt_number = models.CharField(max_length=30, unique=True, blank=True)
    order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name="receipts")
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="goods_receipts")
    receipt_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PARTIAL)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "GoodsReceipt"
        ordering = ["-created_at"]

    def __str__(self):
        return self.receipt_number

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            from django.utils import timezone
            year = timezone.now().year
            count = GoodsReceipt.objects.filter(created_at__year=year).count() + 1
            self.receipt_number = f"GR-{year}-{count:05d}"
        super().save(*args, **kwargs)


class GoodsReceiptLine(models.Model):
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name="lines")
    order_line = models.ForeignKey(OrderLine, on_delete=models.PROTECT)
    pr = models.ForeignKey(
        PurchaseRequisition, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity_ordered = models.DecimalField(max_digits=18, decimal_places=4)
    quantity_received = models.DecimalField(max_digits=18, decimal_places=4)
    unit_of_measure = models.CharField(max_length=50)
    diff_note = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "GoodsReceiptLine"

    @property
    def quantity_diff(self):
        return self.quantity_ordered - self.quantity_received


class DepartmentConfirmation(models.Model):
    receipt_line = models.ForeignKey(GoodsReceiptLine, on_delete=models.PROTECT)
    pr = models.ForeignKey(PurchaseRequisition, on_delete=models.PROTECT)
    confirmed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    confirmed_at = models.DateTimeField(auto_now_add=True)
    quality_note = models.CharField(max_length=500, null=True, blank=True)
    is_confirmed = models.BooleanField(default=True)

    class Meta:
        db_table = "DepartmentConfirmation"
