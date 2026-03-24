from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role(Role.ADMIN)


class IsPurchasing(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_purchasing()


class IsPurchasingManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role(
            Role.PURCHASING_MANAGER, Role.ADMIN
        )


class IsDeptHead(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role(Role.DEPT_HEAD)


class IsApprover(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_approver()


class IsWarehouseKeeper(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role(Role.WAREHOUSE_KEEPER)


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_role(Role.ACCOUNTANT)


class IsAdminOrPurchasing(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_purchasing() or request.user.has_role(Role.ADMIN)
        )
