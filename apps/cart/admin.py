from django.contrib import admin
from .models import Cart, CartItem, PurchaseOrder, OrderLine, OrderSupplier


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["added_by", "added_at", "removed_at"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["cart_title", "created_by", "status", "created_at"]
    list_filter = ["status"]
    inlines = [CartItemInline]


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "created_by", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["order_number"]
    inlines = [OrderLineInline]
