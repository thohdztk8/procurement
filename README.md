# 🏭 Procurement System — Hệ thống Quản lý Mua hàng

> Django 5 · SQL Server · Docker · REST API · Celery

Hệ thống quản lý toàn bộ quy trình mua hàng cho doanh nghiệp sản xuất: từ yêu cầu mua hàng (PR) → giỏ hàng → đơn hàng → báo giá → IPO → nhập kho → thanh toán.

---

## 📐 Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                          │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────────┐  │
│  │  nginx   │──▶│  django  │──▶│  mssql   │   │   redis    │  │
│  │ :80      │   │ :8000    │   │  :1433   │   │  :6379     │  │
│  └──────────┘   └──────────┘   └──────────┘   └────────────┘  │
│                      │                              │           │
│                 ┌────┴─────┐                   ┌───┴────┐      │
│                 │  celery  │◀──────────────────▶│ broker │      │
│                 │  worker  │                   └────────┘      │
│                 └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu trúc project

```
procurement/
├── config/                     # Django project config
│   ├── settings.py             # Cấu hình toàn hệ thống
│   ├── urls.py                 # Route tổng
│   ├── celery.py               # Celery app
│   └── wsgi.py
├── apps/
│   ├── authentication/         # Module 1 — Xác thực & Phân quyền (RBAC)
│   │   ├── models.py           # Department, Role, User, UserSession
│   │   ├── serializers.py
│   │   ├── views.py            # Login, Logout, User CRUD, Me
│   │   ├── permissions.py      # IsAdmin, IsDeptHead, IsApprover, ...
│   │   └── management/commands/
│   │       ├── seed_roles.py   # Khởi tạo roles & admin mặc định
│   │       └── wait_for_db.py  # Chờ DB sẵn sàng
│   │
│   ├── master_data/            # Module 2 — Danh mục (vật tư, NCC)
│   │   └── models.py           # ItemCategory, Item, Supplier, SupplierContact
│   │
│   ├── requisition/            # Module 3 — Yêu cầu mua hàng (PR)
│   │   └── models.py           # PurchaseRequisition, PRHistory
│   │
│   ├── cart/                   # Module 4 — Giỏ hàng & Đơn hàng
│   │   ├── models.py           # Cart, CartItem, PurchaseOrder, OrderLine, ...
│   │   └── services.py         # CartService, OrderService
│   │
│   ├── quotation/              # Module 5 — Báo giá
│   │   ├── models.py           # QuotationSession, QuotationLine
│   │   ├── services.py         # QuotationService
│   │   ├── portal_views.py     # Public supplier portal (no auth)
│   │   └── portal_urls.py
│   │
│   ├── ipo/                    # Module 6 — IPO & Phê duyệt
│   │   ├── models.py           # IPO, IPOLine, IPOHistory
│   │   └── services.py         # IPOService (create, submit, approve, reject)
│   │
│   ├── warehouse/              # Module 7 — Kho
│   │   ├── models.py           # GoodsReceipt, GoodsReceiptLine, DepartmentConfirmation
│   │   └── services.py         # WarehouseService
│   │
│   ├── finance/                # Module 8 — Hóa đơn & Thanh toán
│   │   └── models.py           # Invoice, PaymentRequest, Payment, CreditNote
│   │
│   ├── notifications/          # Module 9 — Thông báo
│   │   ├── models.py           # Notification
│   │   ├── services.py         # NotificationService
│   │   └── tasks.py            # Celery tasks (email async)
│   │
│   ├── reports/                # Module 10 — Báo cáo & Thống kê
│   │   └── views.py            # PO Status, NCC Performance, Spend, Dashboard
│   │
│   └── audit_log/              # Audit trail
│       └── models.py           # AuditLog
│
├── docker/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── init-db.sh
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── manage.py
```

---

## 🔑 Luồng nghiệp vụ

```
Trưởng BP        Mua hàng             Giám đốc    Thủ kho     Kế toán
   │                │                     │           │           │
   │──[Tạo PR]─────▶│                     │           │           │
   │                │──[Thêm vào Cart]     │           │           │
   │                │──[Tạo Order]         │           │           │
   │                │──[Gửi báo giá]──────────────────────────────▶NCC
   │                │                                              │
   │                │◀──────────[NCC submit báo giá qua link]──────│
   │                │──[Chốt giá → Tạo IPO]                        │
   │                │──[Submit duyệt]──────▶│                      │
   │                │                       │──[Approve/Reject]    │
   │                │◀──[Notification]───────│                      │
   │                │──[Confirm in-progress]                       │
   │                │                                 │            │
   │◀──[Nhận hàng]──────────────────────────[Nhập kho]│            │
   │──[Xác nhận]───▶│                                              │
   │                │──[Upload hóa đơn]                            │
   │                │──[Tạo yêu cầu TT]───────────────────────────▶│
   │                │                                              │──[Thanh toán]
   │                │                                              │──[Đóng invoice]
```

---

## 🚀 Cài đặt & Chạy

### Yêu cầu
- Docker Desktop ≥ 4.x
- Docker Compose ≥ 2.x

### Bước 1 — Clone & cấu hình môi trường

```bash
git clone <repo-url> procurement
cd procurement

# Tạo file .env từ template
cp .env.example .env

# Chỉnh sửa .env với thông tin thực tế
# Tối thiểu cần đặt:
#   SECRET_KEY=<random-string>
#   MSSQL_SA_PASSWORD=<strong-password>
nano .env
```

### Bước 2 — Build & khởi động

```bash
# Build images và chạy tất cả services
docker compose up --build -d

# Theo dõi log
docker compose logs -f web

# Kiểm tra trạng thái
docker compose ps
```

> Lần đầu chạy: Django sẽ tự động `migrate`, seed roles, và tạo tài khoản admin.

### Bước 3 — Truy cập

| Service | URL |
|---------|-----|
| REST API | http://localhost/api/ |
| Swagger UI | http://localhost/api/docs/ |
| Django Admin | http://localhost/admin/ |
| Supplier Portal | http://localhost/portal/quotation/{token}/ |

**Tài khoản admin mặc định:**
- Email: `admin@procurement.local`
- Password: `Admin@123456`
- ⚠️ Đổi mật khẩu ngay sau lần đăng nhập đầu

---

## 🔐 Phân quyền (RBAC)

| Role | Mã | Quyền chính |
|------|----|-------------|
| Giám đốc | `DIRECTOR` | Phê duyệt IPO, xem tất cả báo cáo |
| Phó GĐ | `VICE_DIRECTOR` | Tương tự Giám đốc |
| Trưởng phòng MH | `PURCHASING_MANAGER` | Quản lý cart, order, IPO, báo cáo |
| Nhân viên MH | `PURCHASING_STAFF` | Tạo cart/order, gửi báo giá, cập nhật TT |
| Trưởng bộ phận | `DEPT_HEAD` | Tạo/hủy PR, xác nhận nhận hàng |
| Thủ kho | `WAREHOUSE_KEEPER` | Nhập kho, xem phiếu nhận |
| Kế toán | `ACCOUNTANT` | Xem hóa đơn, xử lý thanh toán |
| Quản trị viên | `ADMIN` | Quản lý người dùng, danh mục, cấu hình |

---

## 📡 API Reference

### Authentication

```http
POST /api/auth/login/
POST /api/auth/logout/
POST /api/auth/token/refresh/
GET  /api/auth/me/
POST /api/auth/change-password/
```

### Master Data

```http
GET/POST   /api/master/items/
GET/PUT    /api/master/items/{id}/
GET/POST   /api/master/suppliers/
GET/POST   /api/master/suppliers/{id}/contacts/
```

### Purchase Requisition

```http
GET/POST   /api/requisitions/
GET/PUT    /api/requisitions/{id}/
POST       /api/requisitions/{id}/cancel/
```

### Cart & Order

```http
GET/POST   /api/carts/
POST       /api/carts/{id}/add-pr/
POST       /api/carts/{id}/remove-pr/{pr_id}/
POST       /api/carts/orders/create/
GET        /api/carts/orders/
POST       /api/carts/orders/{id}/update-status/
```

### Quotation

```http
POST       /api/quotations/send/
GET        /api/quotations/sessions/
POST       /api/quotations/orders/{id}/select/

# Public (no auth — supplier portal)
GET        /portal/quotation/{token}/
POST       /portal/quotation/{token}/submit/
```

### IPO

```http
GET        /api/ipos/
POST       /api/ipos/create/
GET        /api/ipos/{id}/
POST       /api/ipos/{id}/submit/
POST       /api/ipos/{id}/approve/        # Director only
POST       /api/ipos/{id}/reject/         # Director only
POST       /api/ipos/{id}/confirm-in-progress/
```

### Warehouse

```http
GET/POST   /api/warehouse/receipts/
POST       /api/warehouse/receipt-lines/{id}/confirm/
```

### Finance

```http
GET/POST   /api/finance/invoices/
GET/POST   /api/finance/payment-requests/
GET/POST   /api/finance/payments/
GET/POST   /api/finance/credit-notes/
```

### Reports

```http
GET        /api/reports/po-status/
GET        /api/reports/supplier-performance/
GET        /api/reports/spend-by-category/
GET        /api/reports/accounts-payable/
GET        /api/reports/dashboard/         # Director only
GET        /api/reports/export/po/         # Returns Excel file
```

---

## ⚙️ Quản lý Docker

```bash
# Dừng tất cả
docker compose down

# Xóa volumes (reset data)
docker compose down -v

# Rebuild image sau khi thay đổi code
docker compose up --build web

# Chạy management command
docker compose exec web python manage.py <command>

# Vào shell Django
docker compose exec web python manage.py shell

# Xem log từng service
docker compose logs -f celery
docker compose logs -f db

# Backup database
docker compose exec db /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -No \
  -Q "BACKUP DATABASE ProcurementDB TO DISK='/var/opt/mssql/backup/procurement.bak'"
```

---

## 🗄️ Database Schemas

| Schema | Nội dung |
|--------|----------|
| `auth` | Department, Role, Users, UserSession |
| `master_data` | ItemCategory, Item, Supplier, SupplierContact |
| `pr` | PurchaseRequisition, PRHistory |
| `cart` | Cart, CartItem, PurchaseOrder, OrderLine, OrderSupplier |
| `quot` | QuotationSession, QuotationLine |
| `ipo` | IPO, IPOLine, IPOHistory |
| `wh` | GoodsReceipt, GoodsReceiptLine, DepartmentConfirmation |
| `fin` | Invoice, PaymentRequest, Payment, CreditNote |
| `dbo` | Notification |
| `audit` | AuditLog |

---

## 🔧 Cấu hình nâng cao

### Cloud Storage (AWS S3)

```env
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=procurement-files
AWS_S3_REGION_NAME=ap-southeast-1
```

### Email SMTP (Gmail)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Thời hạn link báo giá NCC

```env
QUOTATION_TOKEN_EXPIRY_HOURS=72    # mặc định 72 giờ
```

---

## 📦 Dependencies chính

| Package | Phiên bản | Mục đích |
|---------|-----------|----------|
| Django | 5.1.4 | Web framework |
| mssql-django | 1.5 | SQL Server ORM backend |
| djangorestframework | 3.15 | REST API |
| simplejwt | 5.3 | JWT authentication |
| celery | 5.4 | Async task queue |
| redis | 5.2 | Cache & message broker |
| openpyxl | 3.1 | Excel export |
| reportlab | 4.2 | PDF generation |
| drf-spectacular | 0.28 | OpenAPI/Swagger docs |

---

## 🐞 Troubleshooting

**DB connection refused:**
```bash
# Kiểm tra SQL Server đã healthy chưa
docker compose ps db
docker compose logs db | tail -20
```

**Migration lỗi:**
```bash
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py migrate --run-syncdb
```

**Celery không nhận task:**
```bash
docker compose restart celery
docker compose logs celery
```

**Reset toàn bộ dữ liệu:**
```bash
docker compose down -v
docker compose up --build -d
```

---

## 📄 Tài liệu tham chiếu

- URD v1.0 — 23/03/2026
- Use-Case Document v1.0 — 23/03/2026
- DB Design v1.0 — SQL Server

---

*Procurement System v1.0 — Built with Django 5 & Docker*
