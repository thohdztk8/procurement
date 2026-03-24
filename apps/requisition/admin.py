from django.contrib import admin
from .models import PurchaseRequisition, PRHistory


class PRHistoryInline(admin.TabularInline):
    model = PRHistory
    extra = 0
    readonly_fields = ["changed_by", "change_type", "field_changed", "old_value", "new_value", "changed_at"]


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = ["pr_number", "department", "requested_by", "get_item_name", "quantity", "priority", "status", "created_at"]
    list_filter = ["status", "priority", "department"]
    search_fields = ["pr_number", "item__item_name", "item_name_free_text"]
    readonly_fields = ["pr_number", "created_at", "updated_at"]
    inlines = [PRHistoryInline]
