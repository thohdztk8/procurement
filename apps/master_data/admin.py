from django.contrib import admin
from .models import ItemCategory, Item, Supplier, SupplierContact


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ["category_code", "category_name", "is_active"]
    search_fields = ["category_code", "category_name"]


class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["item_code", "item_name", "unit_of_measure", "category", "is_active"]
    search_fields = ["item_code", "item_name"]
    list_filter = ["category", "is_active"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["supplier_code", "company_name", "tax_code", "status", "payment_term_days"]
    search_fields = ["supplier_code", "company_name", "tax_code"]
    list_filter = ["status"]
    inlines = [SupplierContactInline]
