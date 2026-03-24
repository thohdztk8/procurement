"""
Module: Authentication
Tables: Department, Role, User, UserSession
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class Department(models.Model):
    department_code = models.CharField(max_length=20, unique=True)
    department_name = models.CharField(max_length=150)
    branch_location = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Department"
        ordering = ["department_name"]

    def __str__(self):
        return f"{self.department_code} — {self.department_name}"


class Role(models.Model):
    DIRECTOR = "DIRECTOR"
    VICE_DIRECTOR = "VICE_DIRECTOR"
    PURCHASING_MANAGER = "PURCHASING_MANAGER"
    PURCHASING_STAFF = "PURCHASING_STAFF"
    DEPT_HEAD = "DEPT_HEAD"
    WAREHOUSE_KEEPER = "WAREHOUSE_KEEPER"
    ACCOUNTANT = "ACCOUNTANT"
    ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (DIRECTOR, "Giám đốc"),
        (VICE_DIRECTOR, "Phó Giám đốc"),
        (PURCHASING_MANAGER, "Trưởng phòng Mua hàng"),
        (PURCHASING_STAFF, "Nhân viên Mua hàng"),
        (DEPT_HEAD, "Trưởng bộ phận"),
        (WAREHOUSE_KEEPER, "Thủ kho"),
        (ACCOUNTANT, "Kế toán"),
        (ADMIN, "Quản trị viên"),
    ]

    role_code = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    role_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "Role"

    def __str__(self):
        return self.role_name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=200, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="users", null=True, blank=True
    )
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="users", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    must_change_pass = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_users"
    )

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "User"

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    @property
    def role_code(self):
        return self.role.role_code if self.role else None

    def has_role(self, *role_codes):
        return self.role_code in role_codes

    def is_approver(self):
        return self.has_role(Role.DIRECTOR, Role.VICE_DIRECTOR)

    def is_purchasing(self):
        return self.has_role(Role.PURCHASING_STAFF, Role.PURCHASING_MANAGER)


class UserSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "UserSession"
