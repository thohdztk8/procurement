from django.contrib import admin
from .models import Invoice, PaymentRequest, Payment, CreditNote


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "supplier", "order", "total_amount", "currency", "status", "invoice_date"]
    list_filter = ["status", "currency"]
    search_fields = ["invoice_number"]


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ["request_number", "invoice", "amount", "due_date", "status"]
    list_filter = ["status"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_request", "transaction_ref", "amount_paid", "payment_date", "paid_by"]


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ["credit_note_number", "invoice", "supplier", "amount", "issued_date"]
