from django.contrib import admin
from .models import QuotationSession, QuotationLine


class QuotationLineInline(admin.TabularInline):
    model = QuotationLine
    extra = 0


@admin.register(QuotationSession)
class QuotationSessionAdmin(admin.ModelAdmin):
    list_display = ["order", "order_supplier", "status", "token_expiry", "email_sent_at"]
    list_filter = ["status"]
    inlines = [QuotationLineInline]
