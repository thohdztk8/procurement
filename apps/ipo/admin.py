from django.contrib import admin
from .models import IPO, IPOLine, IPOHistory


class IPOLineInline(admin.TabularInline):
    model = IPOLine
    extra = 0


@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = ["ipo_number", "order", "total_amount", "currency", "status", "created_at"]
    list_filter = ["status", "currency"]
    search_fields = ["ipo_number"]
    inlines = [IPOLineInline]
