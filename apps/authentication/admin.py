from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Department, Role, User, UserSession


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["department_code", "department_name", "branch_location", "is_active"]
    search_fields = ["department_code", "department_name"]
    list_filter = ["is_active"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["role_code", "role_name", "is_active"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "role", "department", "is_active", "must_change_pass"]
    search_fields = ["email", "full_name"]
    list_filter = ["role", "department", "is_active"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Thông tin", {"fields": ("full_name", "department", "role")}),
        ("Quyền", {"fields": ("is_active", "is_staff", "is_superuser", "must_change_pass")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "full_name", "password1", "password2", "role", "department")}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "expires_at", "is_revoked", "ip_address"]
    list_filter = ["is_revoked"]
