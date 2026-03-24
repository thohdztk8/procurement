"""Management command: seed default roles, departments, and superuser."""
from django.core.management.base import BaseCommand
from apps.authentication.models import Role, Department, User


class Command(BaseCommand):
    help = "Seed default roles and initial admin account"

    def handle(self, *args, **options):
        # Roles
        roles_data = [
            ("DIRECTOR", "Giám đốc", "Xem tất cả, phê duyệt IPO, toàn bộ báo cáo"),
            ("VICE_DIRECTOR", "Phó Giám đốc", "Tương tự Giám đốc"),
            ("PURCHASING_MANAGER", "Trưởng phòng Mua hàng", "Quản lý cart, order, IPO, báo cáo"),
            ("PURCHASING_STAFF", "Nhân viên Mua hàng", "Tạo cart, order, gửi báo giá, cập nhật trạng thái"),
            ("DEPT_HEAD", "Trưởng bộ phận", "Tạo/xem PR, xác nhận nhận hàng"),
            ("WAREHOUSE_KEEPER", "Thủ kho", "Nhập kho, xem danh sách hàng cần nhận"),
            ("ACCOUNTANT", "Kế toán", "Xem hóa đơn, xử lý thanh toán, đóng invoice"),
            ("ADMIN", "Quản trị viên", "Quản lý tài khoản, phân quyền, cấu hình hệ thống"),
        ]
        for code, name, desc in roles_data:
            Role.objects.get_or_create(role_code=code, defaults={"role_name": name, "description": desc})
        self.stdout.write(self.style.SUCCESS(f"✓ {len(roles_data)} roles seeded"))

        # Default department
        dept, _ = Department.objects.get_or_create(
            department_code="ADMIN",
            defaults={"department_name": "Quản trị hệ thống", "branch_location": "Trụ sở"}
        )

        # Admin user
        if not User.objects.filter(email="admin@procurement.local").exists():
            admin_role = Role.objects.get(role_code="ADMIN")
            User.objects.create_superuser(
                email="admin@procurement.local",
                password="Admin@123456",
                full_name="System Administrator",
                department=dept,
                role=admin_role,
            )
            self.stdout.write(self.style.SUCCESS("✓ Admin user created: admin@procurement.local / Admin@123456"))
        else:
            self.stdout.write("✓ Admin user already exists")
