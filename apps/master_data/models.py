"""
Module: Master Data
Tables: ItemCategory, Item, Supplier, SupplierContact
"""
from django.db import models
from apps.authentication.models import User


class ItemCategory(models.Model):
    category_code = models.CharField(max_length=20, unique=True)
    category_name = models.CharField(max_length=150)
    description = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ItemCategory"
        ordering = ["category_name"]

    def __str__(self):
        return f"{self.category_code} — {self.category_name}"


class Item(models.Model):
    item_code = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=250)
    description = models.CharField(max_length=1000, null=True, blank=True)
    unit_of_measure = models.CharField(max_length=50)
    category = models.ForeignKey(
        ItemCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_items"
    )

    class Meta:
        db_table = "Item"
        ordering = ["item_name"]

    def __str__(self):
        return f"{self.item_code} — {self.item_name}"


class Supplier(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SUSPENDED = "suspended"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Hoạt động"),
        (STATUS_SUSPENDED, "Tạm dừng"),
    ]

    supplier_code = models.CharField(max_length=30, unique=True)
    company_name = models.CharField(max_length=250)
    tax_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    item_category = models.CharField(max_length=250, null=True, blank=True)
    payment_term_days = models.IntegerField(default=30)
    payment_term_note = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_suppliers"
    )

    class Meta:
        db_table = "Supplier"
        ordering = ["company_name"]

    def __str__(self):
        return f"{self.supplier_code} — {self.company_name}"


class SupplierContact(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="contacts")
    contact_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=30, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "SupplierContact"

    def __str__(self):
        return f"{self.contact_name} ({self.supplier.company_name})"
