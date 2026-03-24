-- ============================================================
-- HỆ THỐNG QUẢN LÝ MUA HÀNG - SQL SERVER DATABASE
-- Phiên bản: 1.0  |  Ngày: 23/03/2026
-- Tham chiếu: URD v1.0 + Use-Case Document v1.0
-- ============================================================

USE master;
GO

IF DB_ID('ProcurementDB') IS NOT NULL
BEGIN
    ALTER DATABASE ProcurementDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE ProcurementDB;
END
GO

CREATE DATABASE ProcurementDB
    COLLATE Vietnamese_CI_AS;
GO

USE ProcurementDB;
GO

-- ============================================================
-- SCHEMA
-- ============================================================
CREATE SCHEMA auth;   -- Xác thực & phân quyền
CREATE SCHEMA master_data; -- Danh mục
CREATE SCHEMA pr;     -- Purchase Requisition
CREATE SCHEMA cart;   -- Giỏ hàng & Order
CREATE SCHEMA quot;   -- Báo giá
CREATE SCHEMA ipo;    -- IPO & phê duyệt
CREATE SCHEMA wh;     -- Kho
CREATE SCHEMA fin;    -- Hóa đơn & thanh toán
CREATE SCHEMA audit;  -- Audit log
GO

-- ============================================================
-- MODULE 1: AUTH — XÁC THỰC & PHÂN QUYỀN
-- ============================================================

-- Bộ phận / chi nhánh
CREATE TABLE auth.Department (
    DepartmentID    INT IDENTITY(1,1) PRIMARY KEY,
    DepartmentCode  NVARCHAR(20)  NOT NULL UNIQUE,
    DepartmentName  NVARCHAR(150) NOT NULL,
    BranchLocation  NVARCHAR(100) NULL,        -- chi nhánh / nhà máy
    IsActive        BIT           NOT NULL DEFAULT 1,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Vai trò hệ thống (RBAC)
CREATE TABLE auth.Role (
    RoleID          INT IDENTITY(1,1) PRIMARY KEY,
    RoleCode        NVARCHAR(50)  NOT NULL UNIQUE,
    RoleName        NVARCHAR(100) NOT NULL,
    Description     NVARCHAR(500) NULL,
    IsActive        BIT           NOT NULL DEFAULT 1
);

-- Người dùng nội bộ
CREATE TABLE auth.Users (
    UserID          INT IDENTITY(1,1) PRIMARY KEY,
    FullName        NVARCHAR(150) NOT NULL,
    Email           NVARCHAR(200) NOT NULL UNIQUE,
    PasswordHash    NVARCHAR(255) NOT NULL,         -- bcrypt hash
    DepartmentID    INT           NOT NULL REFERENCES auth.Department(DepartmentID),
    RoleID          INT           NOT NULL REFERENCES auth.Role(RoleID),
    IsActive        BIT           NOT NULL DEFAULT 1,
    MustChangePass  BIT           NOT NULL DEFAULT 1, -- đổi pass lần đầu
    LastLoginAt     DATETIME2     NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CreatedBy       INT           NULL REFERENCES auth.Users(UserID)
);

-- Phiên đăng nhập
CREATE TABLE auth.UserSession (
    SessionID       UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserID          INT           NOT NULL REFERENCES auth.Users(UserID),
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    ExpiresAt       DATETIME2     NOT NULL,
    IsRevoked       BIT           NOT NULL DEFAULT 0,
    IPAddress       NVARCHAR(50)  NULL,
    UserAgent       NVARCHAR(500) NULL
);

-- ============================================================
-- MODULE 2: MASTER DATA — DANH MỤC
-- ============================================================

-- Nhóm danh mục vật tư
CREATE TABLE master_data.ItemCategory (
    CategoryID      INT IDENTITY(1,1) PRIMARY KEY,
    CategoryCode    NVARCHAR(20)  NOT NULL UNIQUE,
    CategoryName    NVARCHAR(150) NOT NULL,
    Description     NVARCHAR(500) NULL,
    IsActive        BIT           NOT NULL DEFAULT 1,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Danh mục vật tư / sản phẩm (Master Item List)
CREATE TABLE master_data.Item (
    ItemID          INT IDENTITY(1,1) PRIMARY KEY,
    ItemCode        NVARCHAR(50)  NOT NULL UNIQUE,
    ItemName        NVARCHAR(250) NOT NULL,
    Description     NVARCHAR(1000) NULL,
    UnitOfMeasure   NVARCHAR(50)  NOT NULL,          -- kg, chiếc, lít, bộ...
    CategoryID      INT           NULL REFERENCES master_data.ItemCategory(CategoryID),
    IsActive        BIT           NOT NULL DEFAULT 1,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CreatedBy       INT           NULL REFERENCES auth.Users(UserID)
);

-- Nhà cung cấp
CREATE TABLE master_data.Supplier (
    SupplierID      INT IDENTITY(1,1) PRIMARY KEY,
    SupplierCode    NVARCHAR(30)  NOT NULL UNIQUE,
    CompanyName     NVARCHAR(250) NOT NULL,
    TaxCode         NVARCHAR(20)  NULL,              -- mã số thuế
    Address         NVARCHAR(500) NULL,
    ItemCategory    NVARCHAR(250) NULL,              -- nhóm hàng cung cấp
    PaymentTermDays INT           NOT NULL DEFAULT 30, -- Net 30/45/60
    PaymentTermNote NVARCHAR(200) NULL,
    Status          NVARCHAR(20)  NOT NULL DEFAULT 'active'
                        CHECK (Status IN ('active','suspended')),
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CreatedBy       INT           NULL REFERENCES auth.Users(UserID)
);

-- Người liên lạc của nhà cung cấp (1 NCC có nhiều người liên lạc)
CREATE TABLE master_data.SupplierContact (
    ContactID       INT IDENTITY(1,1) PRIMARY KEY,
    SupplierID      INT           NOT NULL REFERENCES master_data.Supplier(SupplierID),
    ContactName     NVARCHAR(150) NOT NULL,
    Email           NVARCHAR(200) NOT NULL,
    Phone           NVARCHAR(30)  NULL,
    Position        NVARCHAR(100) NULL,
    IsPrimary       BIT           NOT NULL DEFAULT 0, -- liên lạc chính
    IsActive        BIT           NOT NULL DEFAULT 1,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- MODULE 3: PR — YÊU CẦU MUA HÀNG
-- ============================================================

CREATE TABLE pr.PurchaseRequisition (
    PRID            INT IDENTITY(1,1) PRIMARY KEY,
    PRNumber        NVARCHAR(30)  NOT NULL UNIQUE,   -- PR-2026-00001
    DepartmentID    INT           NOT NULL REFERENCES auth.Department(DepartmentID),
    RequestedByID   INT           NOT NULL REFERENCES auth.Users(UserID),
    ItemID          INT           NULL REFERENCES master_data.Item(ItemID), -- NULL nếu free text
    ItemNameFreeText NVARCHAR(250) NULL,             -- loại "Other" - free text
    IsOtherItem     BIT           NOT NULL DEFAULT 0,
    Quantity        DECIMAL(18,4) NOT NULL,
    UnitOfMeasure   NVARCHAR(50)  NOT NULL,
    Priority        NVARCHAR(20)  NOT NULL DEFAULT 'normal'
                        CHECK (Priority IN ('normal','urgent')),
    RequiredDate    DATE          NULL,              -- thời hạn cần hàng
    Notes           NVARCHAR(1000) NULL,
    Status          NVARCHAR(30)  NOT NULL DEFAULT 'pending'
                        CHECK (Status IN ('pending','in_cart','processing','received','cancelled')),
    CancelReason    NVARCHAR(500) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Lịch sử thay đổi PR
CREATE TABLE pr.PRHistory (
    HistoryID       INT IDENTITY(1,1) PRIMARY KEY,
    PRID            INT           NOT NULL REFERENCES pr.PurchaseRequisition(PRID),
    ChangedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    ChangeType      NVARCHAR(50)  NOT NULL,          -- created, updated, cancelled, status_changed
    FieldChanged    NVARCHAR(100) NULL,
    OldValue        NVARCHAR(MAX) NULL,
    NewValue        NVARCHAR(MAX) NULL,
    Note            NVARCHAR(500) NULL,
    ChangedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- MODULE 4: CART & ORDER — GIỎ HÀNG & ĐƠN MUA
-- ============================================================

-- Giỏ hàng
CREATE TABLE cart.Cart (
    CartID          INT IDENTITY(1,1) PRIMARY KEY,
    CartTitle       NVARCHAR(200) NOT NULL,
    CreatedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    Status          NVARCHAR(20)  NOT NULL DEFAULT 'open'
                        CHECK (Status IN ('open','converted','closed')),
    Notes           NVARCHAR(500) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Quan hệ Cart - PR (N:N với metadata)
CREATE TABLE cart.CartItem (
    CartItemID      INT IDENTITY(1,1) PRIMARY KEY,
    CartID          INT           NOT NULL REFERENCES cart.Cart(CartID),
    PRID            INT           NOT NULL REFERENCES pr.PurchaseRequisition(PRID),
    QuantityOverride DECIMAL(18,4) NULL,             -- ghi đè SL từ PR (nếu mua hàng sửa)
    ItemNameOverride NVARCHAR(250) NULL,             -- ghi đè tên vật tư
    AddedByID       INT           NOT NULL REFERENCES auth.Users(UserID),
    AddedAt         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    RemovedAt       DATETIME2     NULL,              -- NULL = còn trong cart
    RemovedByID     INT           NULL REFERENCES auth.Users(UserID),
    CONSTRAINT UQ_CartItem UNIQUE (CartID, PRID)     -- mỗi PR chỉ vào 1 cart 1 lần
);

-- Lịch sử thay đổi Cart
CREATE TABLE cart.CartHistory (
    HistoryID       INT IDENTITY(1,1) PRIMARY KEY,
    CartID          INT           NOT NULL REFERENCES cart.Cart(CartID),
    ChangedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    ChangeType      NVARCHAR(50)  NOT NULL,          -- item_added, item_removed, item_modified
    PRID            INT           NULL REFERENCES pr.PurchaseRequisition(PRID),
    OldValue        NVARCHAR(MAX) NULL,
    NewValue        NVARCHAR(MAX) NULL,
    ChangedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Đơn mua hàng (Order / Purchase Order)
CREATE TABLE cart.PurchaseOrder (
    OrderID         INT IDENTITY(1,1) PRIMARY KEY,
    OrderNumber     NVARCHAR(30)  NOT NULL UNIQUE,   -- PO-2026-00001
    CartID          INT           NOT NULL REFERENCES cart.Cart(CartID),
    CreatedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    Status          NVARCHAR(30)  NOT NULL DEFAULT 'draft'
                        CHECK (Status IN ('draft','quotation_sent','quotation_received',
                                         'ipo_draft','ipo_pending','ipo_approved',
                                         'ipo_rejected','in_progress','delivered',
                                         'partial_delivered','cancelled')),
    Notes           NVARCHAR(1000) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Dòng hàng trong Order (tổng hợp từ các PR cùng item)
CREATE TABLE cart.OrderLine (
    OrderLineID     INT IDENTITY(1,1) PRIMARY KEY,
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    ItemID          INT           NULL REFERENCES master_data.Item(ItemID),
    ItemNameDisplay NVARCHAR(250) NOT NULL,          -- tên hiển thị (từ item hoặc free text)
    UnitOfMeasure   NVARCHAR(50)  NOT NULL,
    TotalQuantity   DECIMAL(18,4) NOT NULL,          -- tổng SL từ tất cả PR
    Notes           NVARCHAR(500) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Mapping OrderLine ↔ PR (nhiều PR tạo nên 1 OrderLine)
CREATE TABLE cart.OrderLinePR (
    OrderLinePRID   INT IDENTITY(1,1) PRIMARY KEY,
    OrderLineID     INT           NOT NULL REFERENCES cart.OrderLine(OrderLineID),
    PRID            INT           NOT NULL REFERENCES pr.PurchaseRequisition(PRID),
    Quantity        DECIMAL(18,4) NOT NULL
);

-- NCC được chọn cho Order (1 Order có thể gửi nhiều NCC)
CREATE TABLE cart.OrderSupplier (
    OrderSupplierID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    SupplierID      INT           NOT NULL REFERENCES master_data.Supplier(SupplierID),
    ContactOverrideName  NVARCHAR(150) NULL,         -- ghi đè tên liên lạc cho order này
    ContactOverrideEmail NVARCHAR(200) NULL,         -- ghi đè email
    AddedByID       INT           NOT NULL REFERENCES auth.Users(UserID),
    AddedAt         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_OrderSupplier UNIQUE (OrderID, SupplierID)
);

-- Lịch sử cập nhật trạng thái Order
CREATE TABLE cart.OrderStatusHistory (
    HistoryID       INT IDENTITY(1,1) PRIMARY KEY,
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    OldStatus       NVARCHAR(30)  NULL,
    NewStatus       NVARCHAR(30)  NOT NULL,
    ChangedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    Note            NVARCHAR(500) NULL,
    ChangedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- MODULE 5: QUOT — BÁO GIÁ
-- ============================================================

-- Phiên báo giá (1 Order có thể mở nhiều phiên)
CREATE TABLE quot.QuotationSession (
    SessionID       INT IDENTITY(1,1) PRIMARY KEY,
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    OrderSupplierID INT           NOT NULL REFERENCES cart.OrderSupplier(OrderSupplierID),
    QuotationToken  NVARCHAR(500) NOT NULL UNIQUE,   -- token bảo mật trong link
    TokenExpiry     DATETIME2     NOT NULL,           -- deadline nhập báo giá
    EmailSentAt     DATETIME2     NULL,
    EmailSentByID   INT           NULL REFERENCES auth.Users(UserID),
    Status          NVARCHAR(20)  NOT NULL DEFAULT 'pending'
                        CHECK (Status IN ('pending','submitted','expired','closed')),
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Báo giá chi tiết theo từng dòng hàng
CREATE TABLE quot.QuotationLine (
    QuotationLineID INT IDENTITY(1,1) PRIMARY KEY,
    SessionID       INT           NOT NULL REFERENCES quot.QuotationSession(SessionID),
    OrderLineID     INT           NOT NULL REFERENCES cart.OrderLine(OrderLineID),
    UnitPrice       DECIMAL(18,4) NULL,              -- đơn giá NCC báo
    TotalPrice      DECIMAL(18,4) NULL,              -- tổng tiền
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    DeliveryDays    INT           NULL,              -- thời gian giao hàng (ngày)
    Notes           NVARCHAR(500) NULL,
    SubmittedAt     DATETIME2     NULL,
    IsSelected      BIT           NOT NULL DEFAULT 0  -- đã được chốt chọn
);

-- Lịch sử submit báo giá (NCC có thể submit nhiều lần)
CREATE TABLE quot.QuotationSubmitHistory (
    SubmitID        INT IDENTITY(1,1) PRIMARY KEY,
    SessionID       INT           NOT NULL REFERENCES quot.QuotationSession(SessionID),
    SubmittedAt     DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    SubmitMethod    NVARCHAR(20)  NOT NULL DEFAULT 'form'
                        CHECK (SubmitMethod IN ('form','excel_upload')),
    IPAddress       NVARCHAR(50)  NULL,
    Notes           NVARCHAR(500) NULL
);

-- ============================================================
-- MODULE 6: IPO — INTERNAL PURCHASE ORDER
-- ============================================================

CREATE TABLE ipo.IPO (
    IPOID           INT IDENTITY(1,1) PRIMARY KEY,
    IPONumber       NVARCHAR(30)  NOT NULL UNIQUE,   -- IPO-2026-00001
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    CreatedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    TotalAmount     DECIMAL(18,4) NOT NULL DEFAULT 0,
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    Status          NVARCHAR(30)  NOT NULL DEFAULT 'draft'
                        CHECK (Status IN ('draft','pending_approval','approved',
                                         'rejected','in_progress','completed')),
    PDFFilePath     NVARCHAR(1000) NULL,             -- đường dẫn file PDF đã ký & upload
    SubmittedAt     DATETIME2     NULL,
    ApprovedAt      DATETIME2     NULL,
    ApprovedByID    INT           NULL REFERENCES auth.Users(UserID),
    RejectedAt      DATETIME2     NULL,
    RejectedByID    INT           NULL REFERENCES auth.Users(UserID),
    RejectionReason NVARCHAR(1000) NULL,
    Notes           NVARCHAR(1000) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Dòng hàng trong IPO (sau khi chốt giá từng item)
CREATE TABLE ipo.IPOLine (
    IPOLineID       INT IDENTITY(1,1) PRIMARY KEY,
    IPOID           INT           NOT NULL REFERENCES ipo.IPO(IPOID),
    OrderLineID     INT           NOT NULL REFERENCES cart.OrderLine(OrderLineID),
    SupplierID      INT           NOT NULL REFERENCES master_data.Supplier(SupplierID),
    QuotationLineID INT           NULL REFERENCES quot.QuotationLine(QuotationLineID),
    ItemNameDisplay NVARCHAR(250) NOT NULL,
    UnitOfMeasure   NVARCHAR(50)  NOT NULL,
    Quantity        DECIMAL(18,4) NOT NULL,
    UnitPrice       DECIMAL(18,4) NOT NULL,
    TotalPrice      DECIMAL(18,4) NOT NULL,
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    PaymentTermDays INT           NOT NULL DEFAULT 30,
    DeliveryDays    INT           NULL,
    Notes           NVARCHAR(500) NULL
);

-- Lịch sử thay đổi IPO
CREATE TABLE ipo.IPOHistory (
    HistoryID       INT IDENTITY(1,1) PRIMARY KEY,
    IPOID           INT           NOT NULL REFERENCES ipo.IPO(IPOID),
    ChangedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    ChangeType      NVARCHAR(50)  NOT NULL,          -- created, updated, submitted, approved, rejected
    OldStatus       NVARCHAR(30)  NULL,
    NewStatus       NVARCHAR(30)  NULL,
    FieldChanged    NVARCHAR(100) NULL,
    OldValue        NVARCHAR(MAX) NULL,
    NewValue        NVARCHAR(MAX) NULL,
    Note            NVARCHAR(500) NULL,
    ChangedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- MODULE 7: WH — NHẬN HÀNG & KHO
-- ============================================================

-- Phiếu nhập kho
CREATE TABLE wh.GoodsReceipt (
    ReceiptID       INT IDENTITY(1,1) PRIMARY KEY,
    ReceiptNumber   NVARCHAR(30)  NOT NULL UNIQUE,   -- GR-2026-00001
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    ReceivedByID    INT           NOT NULL REFERENCES auth.Users(UserID), -- thủ kho
    ReceiptDate     DATE          NOT NULL DEFAULT CAST(SYSUTCDATETIME() AS DATE),
    Status          NVARCHAR(20)  NOT NULL DEFAULT 'partial'
                        CHECK (Status IN ('partial','complete')),
    Notes           NVARCHAR(1000) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Dòng hàng nhập kho
CREATE TABLE wh.GoodsReceiptLine (
    ReceiptLineID   INT IDENTITY(1,1) PRIMARY KEY,
    ReceiptID       INT           NOT NULL REFERENCES wh.GoodsReceipt(ReceiptID),
    OrderLineID     INT           NOT NULL REFERENCES cart.OrderLine(OrderLineID),
    PRID            INT           NULL REFERENCES pr.PurchaseRequisition(PRID), -- bộ phận nhận
    QuantityOrdered DECIMAL(18,4) NOT NULL,
    QuantityReceived DECIMAL(18,4) NOT NULL,
    QuantityDiff    AS (QuantityOrdered - QuantityReceived), -- computed column
    UnitOfMeasure   NVARCHAR(50)  NOT NULL,
    DiffNote        NVARCHAR(500) NULL,              -- ghi chú sai lệch
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Xác nhận nhận hàng từ trưởng bộ phận
CREATE TABLE wh.DepartmentConfirmation (
    ConfirmID       INT IDENTITY(1,1) PRIMARY KEY,
    ReceiptLineID   INT           NOT NULL REFERENCES wh.GoodsReceiptLine(ReceiptLineID),
    PRID            INT           NOT NULL REFERENCES pr.PurchaseRequisition(PRID),
    ConfirmedByID   INT           NOT NULL REFERENCES auth.Users(UserID),
    ConfirmedAt     DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    QualityNote     NVARCHAR(500) NULL,              -- ghi chú chất lượng (tùy chọn)
    IsConfirmed     BIT           NOT NULL DEFAULT 1
);

-- ============================================================
-- MODULE 8: FIN — HÓA ĐƠN & THANH TOÁN
-- ============================================================

-- Hóa đơn từ nhà cung cấp
CREATE TABLE fin.Invoice (
    InvoiceID       INT IDENTITY(1,1) PRIMARY KEY,
    InvoiceNumber   NVARCHAR(50)  NOT NULL,          -- số hóa đơn từ NCC
    OrderID         INT           NOT NULL REFERENCES cart.PurchaseOrder(OrderID),
    SupplierID      INT           NOT NULL REFERENCES master_data.Supplier(SupplierID),
    InvoiceDate     DATE          NOT NULL,
    TotalAmount     DECIMAL(18,4) NOT NULL,
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    PDFFilePath     NVARCHAR(1000) NULL,             -- đường dẫn file PDF hóa đơn
    PDFFileURL      NVARCHAR(1000) NULL,             -- hoặc URL hóa đơn điện tử
    Status          NVARCHAR(30)  NOT NULL DEFAULT 'pending'
                        CHECK (Status IN ('pending','payment_requested','paid','credit_noted')),
    Notes           NVARCHAR(1000) NULL,
    UploadedByID    INT           NOT NULL REFERENCES auth.Users(UserID),
    UploadedAt      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_Invoice UNIQUE (OrderID, InvoiceNumber, SupplierID)
);

-- Yêu cầu thanh toán
CREATE TABLE fin.PaymentRequest (
    PaymentRequestID INT IDENTITY(1,1) PRIMARY KEY,
    RequestNumber   NVARCHAR(30)  NOT NULL UNIQUE,   -- PAYREQ-2026-00001
    InvoiceID       INT           NOT NULL REFERENCES fin.Invoice(InvoiceID),
    IPOID           INT           NOT NULL REFERENCES ipo.IPO(IPOID),
    RequestedByID   INT           NOT NULL REFERENCES auth.Users(UserID),
    Amount          DECIMAL(18,4) NOT NULL,
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    DueDate         DATE          NOT NULL,
    PaymentMethod   NVARCHAR(50)  NULL,              -- chuyển khoản, tiền mặt...
    Status          NVARCHAR(20)  NOT NULL DEFAULT 'pending'
                        CHECK (Status IN ('pending','processing','paid','cancelled')),
    Notes           NVARCHAR(1000) NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Thanh toán thực tế
CREATE TABLE fin.Payment (
    PaymentID       INT IDENTITY(1,1) PRIMARY KEY,
    PaymentRequestID INT          NOT NULL REFERENCES fin.PaymentRequest(PaymentRequestID),
    PaidByID        INT           NOT NULL REFERENCES auth.Users(UserID), -- kế toán
    PaidAt          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    PaymentDate     DATE          NOT NULL,
    TransactionRef  NVARCHAR(100) NOT NULL,          -- số tham chiếu giao dịch
    AmountPaid      DECIMAL(18,4) NOT NULL,
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    Notes           NVARCHAR(1000) NULL
);

-- Credit Note (trả hàng / hoàn tiền)
CREATE TABLE fin.CreditNote (
    CreditNoteID    INT IDENTITY(1,1) PRIMARY KEY,
    CreditNoteNumber NVARCHAR(50) NOT NULL UNIQUE,
    InvoiceID       INT           NOT NULL REFERENCES fin.Invoice(InvoiceID),
    SupplierID      INT           NOT NULL REFERENCES master_data.Supplier(SupplierID),
    Amount          DECIMAL(18,4) NOT NULL,
    Currency        NVARCHAR(10)  NOT NULL DEFAULT 'VND',
    Reason          NVARCHAR(500) NOT NULL,
    IssuedDate      DATE          NOT NULL,
    CreatedByID     INT           NOT NULL REFERENCES auth.Users(UserID),
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- MODULE 9: NOTIFICATIONS — THÔNG BÁO
-- ============================================================

CREATE TABLE dbo.Notification (
    NotificationID  INT IDENTITY(1,1) PRIMARY KEY,
    RecipientUserID INT           NOT NULL REFERENCES auth.Users(UserID),
    EventType       NVARCHAR(100) NOT NULL,
    -- Ví dụ: pr_created, pr_cancelled, quotation_submitted,
    --        ipo_pending_approval, ipo_approved, ipo_rejected,
    --        goods_received, payment_request_created
    Title           NVARCHAR(200) NOT NULL,
    Message         NVARCHAR(2000) NULL,
    EntityType      NVARCHAR(50)  NULL,              -- PR, Order, IPO, Invoice...
    EntityID        INT           NULL,              -- ID của đối tượng liên quan
    IsRead          BIT           NOT NULL DEFAULT 0,
    IsEmailSent     BIT           NOT NULL DEFAULT 0,
    EmailSentAt     DATETIME2     NULL,
    CreatedAt       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- MODULE 10: AUDIT — NHẬT KÝ HỆ THỐNG
-- ============================================================

CREATE TABLE audit.AuditLog (
    AuditID         BIGINT IDENTITY(1,1) PRIMARY KEY,
    UserID          INT           NULL REFERENCES auth.Users(UserID),
    Action          NVARCHAR(100) NOT NULL,          -- INSERT, UPDATE, DELETE, LOGIN, LOGOUT...
    TableName       NVARCHAR(100) NULL,
    RecordID        INT           NULL,
    OldData         NVARCHAR(MAX) NULL,              -- JSON snapshot trước
    NewData         NVARCHAR(MAX) NULL,              -- JSON snapshot sau
    IPAddress       NVARCHAR(50)  NULL,
    ActionAt        DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================================
-- INDEXES — TỐI ƯU TRUY VẤN
-- ============================================================

-- auth
CREATE INDEX IX_Users_Email          ON auth.Users(Email);
CREATE INDEX IX_Users_Department     ON auth.Users(DepartmentID);
CREATE INDEX IX_UserSession_UserID   ON auth.UserSession(UserID);
CREATE INDEX IX_UserSession_Expiry   ON auth.UserSession(ExpiresAt) WHERE IsRevoked = 0;

-- master_data
CREATE INDEX IX_Item_Category        ON master_data.Item(CategoryID);
CREATE INDEX IX_Item_Name            ON master_data.Item(ItemName);
CREATE INDEX IX_Supplier_Status      ON master_data.Supplier(Status);
CREATE INDEX IX_SupplierContact_Sup  ON master_data.SupplierContact(SupplierID);

-- pr
CREATE INDEX IX_PR_Status            ON pr.PurchaseRequisition(Status);
CREATE INDEX IX_PR_Department        ON pr.PurchaseRequisition(DepartmentID);
CREATE INDEX IX_PR_RequestedBy       ON pr.PurchaseRequisition(RequestedByID);
CREATE INDEX IX_PR_CreatedAt         ON pr.PurchaseRequisition(CreatedAt DESC);
CREATE INDEX IX_PRHistory_PRID       ON pr.PRHistory(PRID);

-- cart
CREATE INDEX IX_Cart_Status          ON cart.Cart(Status);
CREATE INDEX IX_CartItem_CartID      ON cart.CartItem(CartID);
CREATE INDEX IX_CartItem_PRID        ON cart.CartItem(PRID);
CREATE INDEX IX_Order_Status         ON cart.PurchaseOrder(Status);
CREATE INDEX IX_OrderLine_OrderID    ON cart.OrderLine(OrderID);
CREATE INDEX IX_OrderSupplier_Order  ON cart.OrderSupplier(OrderID);
CREATE INDEX IX_OrderSupplier_Sup    ON cart.OrderSupplier(SupplierID);

-- quot
CREATE INDEX IX_QuotSession_Order    ON quot.QuotationSession(OrderID);
CREATE INDEX IX_QuotSession_Token    ON quot.QuotationSession(QuotationToken);
CREATE INDEX IX_QuotSession_Expiry   ON quot.QuotationSession(TokenExpiry);
CREATE INDEX IX_QuotLine_Session     ON quot.QuotationLine(SessionID);

-- ipo
CREATE INDEX IX_IPO_Order            ON ipo.IPO(OrderID);
CREATE INDEX IX_IPO_Status           ON ipo.IPO(Status);
CREATE INDEX IX_IPOLine_IPO          ON ipo.IPOLine(IPOID);
CREATE INDEX IX_IPOHistory_IPO       ON ipo.IPOHistory(IPOID);

-- wh
CREATE INDEX IX_Receipt_Order        ON wh.GoodsReceipt(OrderID);
CREATE INDEX IX_ReceiptLine_Receipt  ON wh.GoodsReceiptLine(ReceiptID);
CREATE INDEX IX_DeptConfirm_PR       ON wh.DepartmentConfirmation(PRID);

-- fin
CREATE INDEX IX_Invoice_Order        ON fin.Invoice(OrderID);
CREATE INDEX IX_Invoice_Supplier     ON fin.Invoice(SupplierID);
CREATE INDEX IX_Invoice_Status       ON fin.Invoice(Status);
CREATE INDEX IX_PayReq_Invoice       ON fin.PaymentRequest(InvoiceID);
CREATE INDEX IX_PayReq_Status        ON fin.PaymentRequest(Status);
CREATE INDEX IX_Payment_PayReq       ON fin.Payment(PaymentRequestID);

-- notification
CREATE INDEX IX_Notif_Recipient      ON dbo.Notification(RecipientUserID, IsRead);
CREATE INDEX IX_Notif_EntityType     ON dbo.Notification(EntityType, EntityID);

-- audit
CREATE INDEX IX_Audit_UserID         ON audit.AuditLog(UserID);
CREATE INDEX IX_Audit_Table          ON audit.AuditLog(TableName, RecordID);
CREATE INDEX IX_Audit_ActionAt       ON audit.AuditLog(ActionAt DESC);

-- ============================================================
-- SEED DATA — DỮ LIỆU MẪU BAN ĐẦU
-- ============================================================

-- Vai trò
INSERT INTO auth.Role (RoleCode, RoleName, Description) VALUES
('DIRECTOR',         N'Giám đốc',                N'Xem tất cả, phê duyệt IPO, toàn bộ báo cáo'),
('DEPUTY_DIRECTOR',  N'Phó giám đốc',             N'Tương tự Giám đốc, có thể giới hạn theo cấu hình'),
('PURCHASING_MANAGER',N'Trưởng phòng mua hàng',   N'Quản lý cart, order, IPO, báo cáo'),
('PURCHASING_STAFF', N'Nhân viên mua hàng',        N'Tạo cart, order, gửi báo giá, cập nhật trạng thái'),
('DEPT_HEAD',        N'Trưởng bộ phận',            N'Tạo/xem PR của bộ phận mình, xác nhận nhận hàng'),
('WAREHOUSE',        N'Thủ kho',                  N'Nhập kho theo order đã duyệt'),
('ACCOUNTANT',       N'Kế toán',                  N'Xem hóa đơn, xử lý thanh toán, đóng invoice'),
('ADMIN',            N'Quản trị viên',             N'Quản lý tài khoản, phân quyền, cấu hình hệ thống');

-- Bộ phận
INSERT INTO auth.Department (DepartmentCode, DepartmentName, BranchLocation) VALUES
('MGMT',   N'Ban giám đốc',       N'Trụ sở chính'),
('PUR',    N'Phòng mua hàng',     N'Trụ sở chính'),
('PROD_A', N'Sản xuất - Nhà máy A', N'Nhà máy A'),
('PROD_B', N'Sản xuất - Nhà máy B', N'Nhà máy B'),
('WH_A',   N'Kho - Nhà máy A',    N'Nhà máy A'),
('WH_B',   N'Kho - Nhà máy B',    N'Nhà máy B'),
('FIN',    N'Phòng Kế toán',      N'Trụ sở chính'),
('IT',     N'Phòng IT / Admin',   N'Trụ sở chính');

-- Nhóm danh mục vật tư
INSERT INTO master_data.ItemCategory (CategoryCode, CategoryName, Description) VALUES
('RAW',     N'Nguyên vật liệu',     N'Nguyên liệu đầu vào sản xuất'),
('PKG',     N'Bao bì',             N'Bao bì đóng gói sản phẩm'),
('CONS',    N'Vật tư tiêu hao',    N'Vật tư sử dụng hàng ngày'),
('EQUIP',   N'Máy móc thiết bị',   N'Thiết bị sản xuất, công cụ'),
('SVC',     N'Dịch vụ thuê ngoài', N'Dịch vụ, gia công'),
('OTHER',   N'Khác',               N'Phân loại khác chưa được liệt kê');

GO

-- ============================================================
-- STORED PROCEDURES HỮU ÍCH
-- ============================================================

-- SP: Sinh số PR tự động
CREATE OR ALTER PROCEDURE pr.usp_GeneratePRNumber
    @PRNumber NVARCHAR(30) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Year CHAR(4) = CAST(YEAR(SYSUTCDATETIME()) AS CHAR(4));
    DECLARE @Seq INT;
    SELECT @Seq = ISNULL(MAX(CAST(RIGHT(PRNumber,5) AS INT)), 0) + 1
    FROM pr.PurchaseRequisition
    WHERE PRNumber LIKE 'PR-' + @Year + '-%';
    SET @PRNumber = 'PR-' + @Year + '-' + RIGHT('00000' + CAST(@Seq AS VARCHAR), 5);
END;
GO

-- SP: Sinh số Order tự động
CREATE OR ALTER PROCEDURE cart.usp_GenerateOrderNumber
    @OrderNumber NVARCHAR(30) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Year CHAR(4) = CAST(YEAR(SYSUTCDATETIME()) AS CHAR(4));
    DECLARE @Seq INT;
    SELECT @Seq = ISNULL(MAX(CAST(RIGHT(OrderNumber,5) AS INT)), 0) + 1
    FROM cart.PurchaseOrder
    WHERE OrderNumber LIKE 'PO-' + @Year + '-%';
    SET @OrderNumber = 'PO-' + @Year + '-' + RIGHT('00000' + CAST(@Seq AS VARCHAR), 5);
END;
GO

-- SP: Sinh số IPO tự động
CREATE OR ALTER PROCEDURE ipo.usp_GenerateIPONumber
    @IPONumber NVARCHAR(30) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Year CHAR(4) = CAST(YEAR(SYSUTCDATETIME()) AS CHAR(4));
    DECLARE @Seq INT;
    SELECT @Seq = ISNULL(MAX(CAST(RIGHT(IPONumber,5) AS INT)), 0) + 1
    FROM ipo.IPO
    WHERE IPONumber LIKE 'IPO-' + @Year + '-%';
    SET @IPONumber = 'IPO-' + @Year + '-' + RIGHT('00000' + CAST(@Seq AS VARCHAR), 5);
END;
GO

-- SP: Lấy dashboard thống kê (cho báo cáo)
CREATE OR ALTER PROCEDURE dbo.usp_GetDashboardStats
    @FromDate DATE = NULL,
    @ToDate   DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET @FromDate = ISNULL(@FromDate, CAST(DATEADD(MONTH, -1, SYSUTCDATETIME()) AS DATE));
    SET @ToDate   = ISNULL(@ToDate,   CAST(SYSUTCDATETIME() AS DATE));

    SELECT
        (SELECT COUNT(*) FROM pr.PurchaseRequisition
         WHERE CAST(CreatedAt AS DATE) BETWEEN @FromDate AND @ToDate) AS TotalPR,
        (SELECT COUNT(*) FROM pr.PurchaseRequisition
         WHERE Status = 'pending'
         AND CAST(CreatedAt AS DATE) BETWEEN @FromDate AND @ToDate)   AS PendingPR,
        (SELECT COUNT(*) FROM cart.PurchaseOrder
         WHERE CAST(CreatedAt AS DATE) BETWEEN @FromDate AND @ToDate) AS TotalOrders,
        (SELECT COUNT(*) FROM ipo.IPO
         WHERE Status = 'pending_approval'
         AND CAST(CreatedAt AS DATE) BETWEEN @FromDate AND @ToDate)   AS PendingIPO,
        (SELECT ISNULL(SUM(TotalAmount),0) FROM ipo.IPO
         WHERE Status IN ('approved','in_progress','completed')
         AND CAST(CreatedAt AS DATE) BETWEEN @FromDate AND @ToDate)   AS TotalApprovedValue,
        (SELECT COUNT(*) FROM fin.PaymentRequest
         WHERE Status = 'pending'
         AND CAST(CreatedAt AS DATE) BETWEEN @FromDate AND @ToDate)   AS PendingPayments,
        (SELECT ISNULL(SUM(Amount),0) FROM fin.PaymentRequest
         WHERE Status = 'pending'
         AND DueDate <= CAST(SYSUTCDATETIME() AS DATE))               AS OverduePaymentAmount;
END;
GO

PRINT N'✅ ProcurementDB schema created successfully.';
GO
