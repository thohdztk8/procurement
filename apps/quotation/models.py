"""
Module: Quotation
Tables: QuotationSession, QuotationLine, QuotationSubmitHistory
"""
import uuid
from django.db import models
from apps.authentication.models import User
from apps.cart.models import PurchaseOrder, OrderLine, OrderSupplier


class QuotationSession(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SUBMITTED = "submitted"
    STATUS_EXPIRED = "expired"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ báo giá"),
        (STATUS_SUBMITTED, "Đã submit"),
        (STATUS_EXPIRED, "Hết hạn"),
        (STATUS_CLOSED, "Đã đóng"),
    ]

    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="quotation_sessions")
    order_supplier = models.ForeignKey(OrderSupplier, on_delete=models.CASCADE, related_name="quotation_sessions")
    quotation_token = models.CharField(max_length=500, unique=True, blank=True)
    token_expiry = models.DateTimeField()
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_sent_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_quotations"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "QuotationSession"

    def save(self, *args, **kwargs):
        if not self.quotation_token:
            self.quotation_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def get_portal_url(self):
        from django.conf import settings
        return f"{settings.SITE_URL}/portal/quotation/{self.quotation_token}/"


class QuotationLine(models.Model):
    session = models.ForeignKey(QuotationSession, on_delete=models.CASCADE, related_name="lines")
    order_line = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name="quotation_lines")
    unit_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    total_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    currency = models.CharField(max_length=10, default="VND")
    delivery_days = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        db_table = "QuotationLine"


class QuotationSubmitHistory(models.Model):
    METHOD_FORM = "form"
    METHOD_EXCEL = "excel_upload"
    METHOD_CHOICES = [
        (METHOD_FORM, "Form online"),
        (METHOD_EXCEL, "Upload Excel"),
    ]

    session = models.ForeignKey(QuotationSession, on_delete=models.CASCADE, related_name="submit_history")
    submitted_at = models.DateTimeField(auto_now_add=True)
    submit_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_FORM)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "QuotationSubmitHistory"
