"""
Module: IPO (Internal Purchase Order)
Tables: IPO, IPOLine, IPOHistory
"""
from django.db import models
from apps.authentication.models import User
from apps.cart.models import PurchaseOrder, OrderLine
from apps.master_data.models import Supplier
from apps.quotation.models import QuotationLine


class IPO(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending_approval"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Nháp"),
        (STATUS_PENDING, "Chờ duyệt"),
        (STATUS_APPROVED, "Đã duyệt"),
        (STATUS_REJECTED, "Từ chối"),
        (STATUS_IN_PROGRESS, "Đang thực hiện"),
        (STATUS_COMPLETED, "Hoàn tất"),
    ]

    ipo_number = models.CharField(max_length=30, unique=True, blank=True)
    order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name="ipos")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_ipos")
    total_amount = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    currency = models.CharField(max_length=10, default="VND")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    pdf_file_path = models.CharField(max_length=1000, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_ipos"
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="rejected_ipos"
    )
    rejection_reason = models.CharField(max_length=1000, null=True, blank=True)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "IPO"
        ordering = ["-created_at"]

    def __str__(self):
        return self.ipo_number

    def save(self, *args, **kwargs):
        if not self.ipo_number:
            from django.utils import timezone
            year = timezone.now().year
            count = IPO.objects.filter(created_at__year=year).count() + 1
            self.ipo_number = f"IPO-{year}-{count:05d}"
        super().save(*args, **kwargs)


class IPOLine(models.Model):
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE, related_name="lines")
    order_line = models.ForeignKey(OrderLine, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    quotation_line = models.ForeignKey(
        QuotationLine, on_delete=models.SET_NULL, null=True, blank=True
    )
    item_name_display = models.CharField(max_length=250)
    unit_of_measure = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    unit_price = models.DecimalField(max_digits=18, decimal_places=4)
    total_price = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10, default="VND")
    payment_term_days = models.IntegerField(default=30)
    delivery_days = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "IPOLine"


class IPOHistory(models.Model):
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE, related_name="history")
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    change_type = models.CharField(max_length=50)
    old_status = models.CharField(max_length=30, null=True, blank=True)
    new_status = models.CharField(max_length=30, null=True, blank=True)
    field_changed = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    note = models.CharField(max_length=500, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "IPOHistory"
