from django.contrib import admin
from .models import GoodsReceipt, GoodsReceiptLine, DepartmentConfirmation


class GoodsReceiptLineInline(admin.TabularInline):
    model = GoodsReceiptLine
    extra = 0


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "order", "received_by", "receipt_date", "status"]
    list_filter = ["status"]
    inlines = [GoodsReceiptLineInline]
