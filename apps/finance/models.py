"""
Module: Finance — Invoice & Payment
Tables: Invoice, PaymentRequest, Payment, CreditNote
"""
from django.db import models
from apps.authentication.models import User
from apps.cart.models import PurchaseOrder
from apps.master_data.models import Supplier
from apps.ipo.models import IPO


class Invoice(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAYMENT_REQUESTED = "payment_requested"
    STATUS_PAID = "paid"
    STATUS_CREDIT_NOTED = "credit_noted"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ xử lý"),
        (STATUS_PAYMENT_REQUESTED, "Đã tạo yêu cầu TT"),
        (STATUS_PAID, "Đã thanh toán"),
        (STATUS_CREDIT_NOTED, "Đã hoàn tiền"),
    ]

    invoice_number = models.CharField(max_length=50)
    order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name="invoices")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="invoices")
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10, default="VND")
    pdf_file_path = models.FileField(upload_to="invoices/", null=True, blank=True)
    pdf_file_url = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="uploaded_invoices")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Invoice"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.invoice_number} ({self.supplier.company_name})"


class PaymentRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Chờ xử lý"),
        (STATUS_PROCESSING, "Đang xử lý"),
        (STATUS_PAID, "Đã thanh toán"),
        (STATUS_CANCELLED, "Đã hủy"),
    ]

    request_number = models.CharField(max_length=30, unique=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payment_requests")
    ipo = models.ForeignKey(IPO, on_delete=models.PROTECT, related_name="payment_requests")
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payment_requests")
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10, default="VND")
    due_date = models.DateField()
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PaymentRequest"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.request_number:
            from django.utils import timezone
            year = timezone.now().year
            count = PaymentRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f"PAYREQ-{year}-{count:05d}"
        super().save(*args, **kwargs)


class Payment(models.Model):
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.PROTECT, related_name="payments")
    paid_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments")
    paid_at = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateField()
    transaction_ref = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10, default="VND")
    notes = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = "Payment"


class CreditNote(models.Model):
    credit_note_number = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="credit_notes")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="credit_notes")
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10, default="VND")
    reason = models.CharField(max_length=500)
    issued_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="credit_notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CreditNote"
