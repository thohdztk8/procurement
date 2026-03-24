

**USE-CASE DOCUMENT**

**Hệ thống Quản lý Mua hàng**

Doanh nghiệp Sản xuất

| Phiên bản: | 1.0 |
| :---- | :---- |
| **Ngày lập:** | 23/03/2026 |
| **Tham chiếu:** | URD v1.0 — 23/03/2026 |
| **Trạng thái:** | Draft — chờ xác nhận khách hàng |

# **1\. Tổng quan tài liệu**

## **1.1 Mục đích**

Tài liệu này đặc tả các Use-Case (ca sử dụng) của hệ thống Quản lý Mua hàng cho doanh nghiệp sản xuất. Mỗi Use-Case mô tả một tương tác cụ thể giữa Actor với hệ thống để đạt được một mục tiêu nghiệp vụ. Tài liệu được xây dựng dựa trên URD v1.0 và kết quả khảo sát nghiệp vụ cập nhật ngày 26/03/2026.

*Lưu ý: Có hai thay đổi quan trọng so với URD v1.0 — (1) hạ tầng triển khai chuyển từ On-premise sang Cloud; (2) cơ sở dữ liệu chuyển từ MySQL sang SQL Server. Chi tiết tại Phụ lục 4.2.*

## **1.2 Danh sách Actor**

| Actor | Loại | Mô tả |
| :---- | :---- | :---- |
| Trưởng bộ phận | Nội bộ | Tạo PR, xác nhận nhận hàng |
| Nhân viên mua hàng | Nội bộ | Quản lý cart, order, báo giá, IPO, hóa đơn, thanh toán |
| Trưởng phòng mua hàng | Nội bộ | Giám sát mua hàng, thực hiện IPO sau duyệt, báo cáo |
| Giám đốc / Phó GĐ | Nội bộ | Phê duyệt IPO, xem báo cáo tổng hợp |
| Thủ kho | Nội bộ | Nhập hàng vào kho theo order đã duyệt |
| Kế toán | Nội bộ | Xử lý hóa đơn, thực hiện thanh toán, đóng invoice |
| Nhà cung cấp (NCC) | Bên ngoài | Nhập báo giá qua link token — không cần tài khoản hệ thống |
| Quản trị viên | Nội bộ | Quản lý tài khoản, phân quyền, cấu hình hệ thống |

## **1.3 Danh mục Use-Case**

| Mã UC | Tên Use-Case | Actor chính | Module |
| :---- | :---- | :---- | :---- |
| UC-01 | Đăng nhập hệ thống | Tất cả người dùng nội bộ | Xác thực |
| UC-02 | Quản lý danh mục vật tư | Quản trị viên / Mua hàng | Master Data |
| UC-03 | Quản lý nhà cung cấp | Quản trị viên / Mua hàng | Master Data |
| UC-04 | Quản lý người dùng & phân quyền | Quản trị viên | Master Data |
| UC-05 | Tạo yêu cầu mua hàng (PR) | Trưởng bộ phận | Purchase Requisition |
| UC-06 | Chỉnh sửa / Hủy PR | Trưởng bộ phận | Purchase Requisition |
| UC-07 | Tạo giỏ hàng (Cart) | Nhân viên mua hàng | Cart & Order |
| UC-08 | Chỉnh sửa Cart | Nhân viên mua hàng | Cart & Order |
| UC-09 | Tạo Order & chọn nhà cung cấp | Nhân viên mua hàng | Cart & Order |
| UC-10 | Gửi yêu cầu báo giá | Nhân viên mua hàng | Quotation |
| UC-11 | Nhập báo giá | Nhà cung cấp | Quotation |
| UC-12 | So sánh & chốt báo giá / Xuất IPO | Nhân viên mua hàng | Quotation / IPO |
| UC-13 | Phê duyệt IPO | Giám đốc / Phó GĐ | IPO Approval |
| UC-14 | Thực hiện mua hàng sau duyệt | Trưởng phòng mua hàng | IPO Approval |
| UC-15 | Cập nhật trạng thái đơn hàng | Nhân viên mua hàng | Order Management |
| UC-16 | Nhập kho | Thủ kho | Warehouse |
| UC-17 | Xác nhận nhận hàng | Trưởng bộ phận | Warehouse |
| UC-18 | Nhập hóa đơn | Nhân viên mua hàng | Invoice & Payment |
| UC-19 | Tạo yêu cầu thanh toán | Nhân viên mua hàng | Invoice & Payment |
| UC-20 | Xử lý thanh toán | Kế toán | Invoice & Payment |
| UC-21 | Xem báo cáo & thống kê | Mua hàng / GĐ / Kế toán | Reporting |

# **2\. Đặc tả Use-Case chi tiết**

## **Module 1 — Xác thực**

### **UC-01 — Đăng nhập hệ thống**

| Mã Use-Case | UC-01 |
| :---- | :---- |
| **Tên** | Đăng nhập hệ thống |
| **Actor chính** | Tất cả người dùng nội bộ |
| **Mô tả** | Người dùng đăng nhập bằng email và mật khẩu. Hệ thống xác thực và chuyển hướng theo vai trò RBAC. |
| **Pre-condition** | Tài khoản đã được quản trị viên tạo và kích hoạt. |
| **Post-condition** | Người dùng được xác thực, truy cập giao diện phù hợp vai trò. |
| **Luồng chính** | 1\. Người dùng truy cập trang đăng nhập. 2\. Nhập email và mật khẩu. 3\. Hệ thống xác thực (bcrypt). 4\. Xác định vai trò RBAC. 5\. Chuyển hướng đến dashboard tương ứng. |
| **Luồng ngoại lệ** | 3a. Sai mật khẩu: hiển thị lỗi, cho phép thử lại. 3b. Tài khoản bị khóa: thông báo liên hệ admin. 3c. Email không tồn tại: thông báo lỗi chung (không tiết lộ). |
| **Bảo mật** | Mật khẩu lưu dạng bcrypt hash. Session có thời hạn. |
| **Tham chiếu FR** | FR-01.3 |

## **Module 2 — Quản lý danh mục (Master Data)**

### **UC-02 — Quản lý danh mục vật tư**

| Mã Use-Case | UC-02 |
| :---- | :---- |
| **Tên** | Quản lý danh mục vật tư |
| **Actor chính** | Quản trị viên, Nhân viên mua hàng |
| **Mô tả** | Thêm mới, chỉnh sửa, tìm kiếm và vô hiệu hóa vật tư trong danh mục master. Nền tảng cho việc tạo PR và order. |
| **Pre-condition** | Actor đã đăng nhập và có quyền quản lý master data. |
| **Post-condition** | Vật tư được lưu/cập nhật và có thể chọn khi tạo PR. |
| **Luồng chính** | 1\. Truy cập mục Danh mục vật tư. 2\. Tìm kiếm theo tên hoặc mã (autocomplete). 3a. Thêm mới: nhập mã, tên, mô tả, đơn vị tính, nhóm danh mục → Lưu. 3b. Chỉnh sửa: chọn vật tư → cập nhật → Lưu. 3c. Vô hiệu hóa: chuyển trạng thái sang Ngừng sử dụng. |
| **Luồng ngoại lệ** | 3a-E1. Mã vật tư trùng: thông báo lỗi, yêu cầu đổi mã. |
| **Ghi chú** | Khi tạo PR, nếu vật tư chưa có trong danh mục, cho phép nhập free text (loại "Other"). |
| **Tham chiếu FR** | FR-01.1 |

### **UC-03 — Quản lý nhà cung cấp**

| Mã Use-Case | UC-03 |
| :---- | :---- |
| **Tên** | Quản lý nhà cung cấp |
| **Actor chính** | Quản trị viên, Nhân viên mua hàng |
| **Mô tả** | Thêm mới, chỉnh sửa, tìm kiếm nhà cung cấp. Thông tin NCC dùng khi tạo order và gửi link báo giá. |
| **Pre-condition** | Actor đã đăng nhập và có quyền quản lý NCC. |
| **Post-condition** | Thông tin NCC được lưu và có thể chọn khi tạo order. |
| **Luồng chính** | 1\. Truy cập mục Nhà cung cấp. 2\. Thêm mới: tên công ty, địa chỉ, MST, email, người liên lạc, nhóm hàng, điều khoản thanh toán mặc định. 3\. Chỉnh sửa thông tin liên hệ hoặc điều khoản. 4\. Thay đổi trạng thái: Hoạt động ↔ Tạm dừng. |
| **Luồng ngoại lệ** | 2-E1. MST trùng: cảnh báo có thể trùng NCC đã tồn tại. |
| **Ghi chú** | Có thể lưu nhiều người liên lạc cho một NCC. Email dùng để gửi link báo giá tự động. |
| **Tham chiếu FR** | FR-01.2 |

### **UC-04 — Quản lý người dùng & phân quyền**

| Mã Use-Case | UC-04 |
| :---- | :---- |
| **Tên** | Quản lý người dùng & phân quyền (RBAC) |
| **Actor chính** | Quản trị viên |
| **Mô tả** | Tạo tài khoản, gán vai trò và vô hiệu hóa tài khoản người dùng nội bộ theo mô hình RBAC. |
| **Pre-condition** | Actor là Quản trị viên đã đăng nhập. |
| **Post-condition** | Tài khoản được tạo/cập nhật. Người dùng truy cập đúng chức năng theo vai trò. |
| **Vai trò hệ thống** | Giám đốc: xem tất cả, phê duyệt IPO, toàn bộ báo cáo. Phó GĐ: tương tự Giám đốc (có thể giới hạn theo cấu hình). Trưởng phòng mua hàng: quản lý cart, order, IPO, báo cáo. Nhân viên mua hàng: tạo cart, order, gửi báo giá, cập nhật trạng thái. Trưởng bộ phận: tạo/xem PR của bộ phận mình, xác nhận nhận hàng. Thủ kho: nhập kho, xem danh sách hàng cần nhận. Kế toán: xem hóa đơn, xử lý thanh toán, đóng invoice. |
| **Luồng chính** | 1\. Quản trị viên truy cập Quản lý người dùng. 2\. Thêm người dùng: tên, email, bộ phận, vai trò. 3\. Hệ thống tạo tài khoản, gửi email mật khẩu tạm thời. 4\. Sửa vai trò/bộ phận: cập nhật và lưu. 5\. Vô hiệu hóa: không thể đăng nhập, dữ liệu vẫn giữ. |
| **Luồng ngoại lệ** | 2-E1. Email đã tồn tại: thông báo lỗi trùng. |
| **Tham chiếu FR** | FR-01.3 |

## **Module 3 — Yêu cầu mua hàng (Purchase Requisition)**

### **UC-05 — Tạo yêu cầu mua hàng (PR)**

| Mã Use-Case | UC-05 |
| :---- | :---- |
| **Tên** | Tạo yêu cầu mua hàng (PR) |
| **Actor chính** | Trưởng bộ phận |
| **Mô tả** | Trưởng bộ phận tạo PR cho vật tư cần mua. PR là điểm khởi đầu toàn bộ quy trình mua hàng. |
| **Pre-condition** | Actor đã đăng nhập với vai trò Trưởng bộ phận. |
| **Post-condition** | PR được tạo ở trạng thái Chờ xử lý. Phòng mua hàng nhận thông báo. |
| **Luồng chính** | 1\. Chọn Tạo yêu cầu mua hàng. 2\. Tìm kiếm và chọn vật tư từ danh mục master (autocomplete). 2a. Vật tư chưa có: chọn loại "Other" và nhập tên free text. 3\. Nhập số lượng cần mua và đơn vị tính. 4\. Chọn độ ưu tiên: Thường / Khẩn. 5\. Nhập thời hạn cần hàng và ghi chú (tùy chọn). 6\. Xác nhận Tạo yêu cầu. 7\. Hệ thống tự ghi: bộ phận, người tạo, ngày tạo. Trạng thái: Chờ xử lý. 8\. Gửi thông báo (in-app \+ email) đến phòng mua hàng. |
| **Luồng ngoại lệ** | 3-E1. Số lượng âm hoặc bằng 0: hiển thị lỗi validation. 6-E1. Thiếu trường bắt buộc: highlight trường cần điền. |
| **Trạng thái PR** | Chờ xử lý → Đã vào cart → Đang xử lý → Đã nhận hàng / Đã hủy |
| **Tham chiếu FR** | FR-02.1 |

### **UC-06 — Chỉnh sửa / Hủy PR**

| Mã Use-Case | UC-06 |
| :---- | :---- |
| **Tên** | Chỉnh sửa / Hủy yêu cầu mua hàng |
| **Actor chính** | Trưởng bộ phận |
| **Mô tả** | Trưởng bộ phận chỉnh sửa hoặc hủy PR đã tạo khi chưa được xử lý, hoặc cập nhật khi phòng mua hàng thay đổi thông tin trong cart. |
| **Pre-condition** | PR tồn tại với trạng thái Chờ xử lý. |
| **Post-condition (Sửa)** | PR cập nhật. Lịch sử thay đổi lưu. Phòng mua hàng nhận thông báo. |
| **Post-condition (Hủy)** | PR chuyển trạng thái Đã hủy. Phòng mua hàng nhận thông báo. |
| **Luồng — Chỉnh sửa** | 1\. Mở danh sách PR của mình. 2\. Chọn PR cần sửa (trạng thái Chờ xử lý). 3\. Cập nhật: số lượng, ưu tiên, thời hạn, ghi chú. 4\. Lưu. Hệ thống ghi log (ai, sửa gì, lúc nào). 5\. Gửi thông báo đến phòng mua hàng. |
| **Luồng — Hủy** | 1\. Chọn PR → Hủy yêu cầu. 2\. Nhập lý do hủy (tùy chọn). 3\. Xác nhận. Trạng thái → Đã hủy. 4\. Thông báo gửi đến phòng mua hàng. |
| **Luồng ngoại lệ** | 2-E1. PR đã Đang xử lý trở lên: không cho hủy, hiển thị thông báo. |
| **Tham chiếu FR** | FR-02.2 |

## **Module 4 — Giỏ hàng & Đơn mua (Cart & Order)**

### **UC-07 — Tạo giỏ hàng (Cart)**

| Mã Use-Case | UC-07 |
| :---- | :---- |
| **Tên** | Tạo giỏ hàng (Cart) |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Lọc danh sách PR và gom nhiều PR vào một cart để chuẩn bị tạo order. Có thể có nhiều cart mở cùng lúc. |
| **Pre-condition** | Có ít nhất một PR ở trạng thái Chờ xử lý. |
| **Post-condition** | Cart được tạo với các PR đã chọn. Trạng thái PR chuyển sang Đã vào cart. |
| **Luồng chính** | 1\. Truy cập danh sách PR. 2\. Lọc theo: danh mục vật tư, tên, ngày tạo, bộ phận, trạng thái, độ ưu tiên. 3\. Chọn nhiều PR (multi-select checkbox). 4\. Chọn Thêm vào giỏ hàng. 5\. Chọn cart hiện có hoặc tạo cart mới (nhập tiêu đề). 6\. Hệ thống thêm PR vào cart, cập nhật trạng thái PR → Đã vào cart. |
| **Luồng ngoại lệ** | 3-E1. Không có PR nào được chọn: hiển thị cảnh báo. |
| **Tham chiếu FR** | FR-03.1 |

### **UC-08 — Chỉnh sửa Cart**

| Mã Use-Case | UC-08 |
| :---- | :---- |
| **Tên** | Chỉnh sửa giỏ hàng |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Thêm/bớt PR, chỉnh sửa số lượng hoặc tên vật tư trong cart trước khi tạo order. |
| **Pre-condition** | Cart đang ở trạng thái mở (chưa tạo order). |
| **Post-condition** | Cart cập nhật. Lịch sử thay đổi lưu. Thông báo gửi đến người tạo PR nếu có thay đổi nội dung. |
| **Luồng chính** | 1\. Mở cart. 2a. Thêm PR: tìm kiếm → chọn → thêm vào cart. 2b. Bớt PR: bỏ chọn → PR trở về Chờ xử lý. 2c. Chỉnh sửa số lượng hoặc tên vật tư → Lưu. 3\. Hệ thống ghi log thay đổi. 4\. Gửi thông báo đến người tạo PR nếu thông tin bị thay đổi. |
| **Tham chiếu FR** | FR-03.1 |

### **UC-09 — Tạo Order & chọn nhà cung cấp**

| Mã Use-Case | UC-09 |
| :---- | :---- |
| **Tên** | Tạo Order & chọn nhà cung cấp |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Từ cart đã chuẩn bị, tổng hợp số lượng theo vật tư, chọn NCC sẽ gửi báo giá và tạo order. |
| **Pre-condition** | Cart có ít nhất một PR. Actor sẵn sàng tạo order. |
| **Post-condition** | Order được tạo với danh sách vật tư tổng hợp và NCC. Trạng thái PR → Đang xử lý. |
| **Luồng chính** | 1\. Mở cart → chọn Tạo order. 2\. Hệ thống tổng hợp: mỗi vật tư → tổng SL từ tất cả PR trong cart. 3\. Với mỗi vật tư, chọn danh sách NCC sẽ gửi báo giá (từ danh mục hoặc free text). 4\. Tùy chỉnh thông tin liên hệ NCC nếu cần (email, tên người liên lạc). 5\. Xác nhận tạo order. Hệ thống lưu order, liên kết cart \+ PR. 6\. Trạng thái PR → Đang xử lý. |
| **Luồng ngoại lệ** | 3-E1. Chưa chọn NCC cho một vật tư: cảnh báo, yêu cầu bổ sung. Ghi chú: Có thể tạo nhiều order từ cùng một cart (tách theo nhóm hàng). |
| **Tham chiếu FR** | FR-03.2, FR-03.3 |

## **Module 5 — Báo giá (Quotation)**

### **UC-10 — Gửi yêu cầu báo giá**

| Mã Use-Case | UC-10 |
| :---- | :---- |
| **Tên** | Gửi yêu cầu báo giá đến nhà cung cấp |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Hệ thống sinh link báo giá riêng (có token bảo mật) cho từng NCC và gửi email theo template. Có thể đặt deadline. |
| **Pre-condition** | Order đã được tạo với ít nhất một NCC được chọn. |
| **Post-condition** | Email yêu cầu báo giá gửi đến từng NCC kèm link riêng có token bảo mật. |
| **Luồng chính** | 1\. Mở order → chọn Gửi yêu cầu báo giá. 2\. Xem/chỉnh sửa nội dung email theo template có sẵn. 3\. Đặt deadline báo giá. 4\. Xác nhận gửi. Hệ thống sinh link duy nhất (token) cho từng NCC. 5\. Gửi email đến từng NCC kèm link. 6\. Lưu trạng thái: Đã gửi yêu cầu báo giá. |
| **Luồng thay thế** | 4a. Sinh link thủ công: nhân viên mua hàng tự nhập báo giá thay NCC qua nút Sinh link thủ công. |
| **Tham chiếu FR** | FR-04.1 |

### **UC-11 — Nhập báo giá (Nhà cung cấp)**

| Mã Use-Case | UC-11 |
| :---- | :---- |
| **Tên** | Nhập báo giá |
| **Actor chính** | Nhà cung cấp |
| **Mô tả** | NCC nhận email, mở link (không cần tài khoản) và nhập giá cho từng sản phẩm. Hỗ trợ form web và upload Excel. |
| **Pre-condition** | NCC có link báo giá hợp lệ, chưa hết deadline, order chưa chốt. |
| **Post-condition** | Báo giá được lưu. Phòng mua hàng nhận thông báo. NCC nhận xác nhận. |
| **Luồng chính** | 1\. NCC mở link từ email. 2\. Hệ thống hiển thị danh sách vật tư cần báo giá (tên, SL yêu cầu). 3a. Nhập qua form: điền đơn giá, tổng tiền, ghi chú từng sản phẩm. 3b. Upload Excel: tải template → điền giá → upload file. 4\. Submit. Hệ thống lưu báo giá. 5\. NCC nhận email xác nhận. 6\. Thông báo (in-app \+ email) gửi đến phòng mua hàng. |
| **Luồng thay thế** | 4a. NCC muốn cập nhật: còn deadline và chưa chốt → mở lại link → sửa → Submit lại. |
| **Luồng ngoại lệ** | 1-E1. Link hết deadline: hiển thị thông báo hết hạn, không cho nhập. 1-E2. Order đã chốt: thông báo đơn hàng đã xử lý. 3b-E1. File Excel sai định dạng: thông báo lỗi, hướng dẫn tải template đúng. |
| **Bảo mật** | Link chứa token duy nhất và có hạn. Nội dung báo giá chỉ người có thẩm quyền trong hệ thống mới xem được. |
| **Tham chiếu FR** | FR-04.2 |

### **UC-12 — So sánh & chốt báo giá / Xuất IPO**

| Mã Use-Case | UC-12 |
| :---- | :---- |
| **Tên** | So sánh & chốt báo giá, xuất IPO |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Xem bảng so sánh giá từ các NCC, chốt NCC cho từng vật tư, tổng hợp và xuất IPO dạng PDF để ký. |
| **Pre-condition** | Ít nhất một NCC đã submit báo giá cho order. |
| **Post-condition** | Vật tư được chốt NCC. IPO được tạo ở trạng thái Draft. File PDF xuất thành công. |
| **Luồng chính** | 1\. Mở màn hình So sánh báo giá của order. 2\. Hệ thống hiển thị bảng so sánh: mỗi vật tư — giá từ các NCC đã báo. 3\. Với từng vật tư, chọn NCC trúng giá → Chốt. 4\. Có thể chốt từng vật tư riêng lẻ. 5\. Sau khi chốt đủ, chọn Xuất IPO. Hệ thống tổng hợp: vật tư, SL, đơn giá, tổng, NCC, điều khoản TT. 6\. Xuất file PDF IPO → in, ký tay, scan → upload file PDF đã ký vào hệ thống. 7\. Trạng thái IPO: Draft. |
| **Luồng thay thế** | 5a. Chỉnh sửa IPO trước khi submit duyệt: cập nhật lại → hệ thống lưu lịch sử. |
| **Tham chiếu FR** | FR-04.3, FR-05.1 |

## **Module 6 — Phê duyệt IPO**

### **UC-13 — Phê duyệt IPO**

| Mã Use-Case | UC-13 |
| :---- | :---- |
| **Tên** | Phê duyệt IPO |
| **Actor chính** | Giám đốc / Phó Giám đốc |
| **Mô tả** | Nhận thông báo IPO chờ duyệt, xem chi tiết và ra quyết định phê duyệt hoặc từ chối. |
| **Pre-condition** | IPO ở trạng thái Chờ duyệt. Giám đốc đã đăng nhập. |
| **Post-condition (Duyệt)** | IPO → Đã duyệt. Phòng mua hàng nhận thông báo để liên hệ NCC. |
| **Post-condition (Từ chối)** | IPO → Từ chối. Phòng mua hàng nhận thông báo \+ lý do. |
| **Luồng — Phê duyệt** | 1\. Nhận thông báo IPO chờ duyệt (in-app \+ email). 2\. Mở IPO, xem chi tiết: vật tư, đơn giá, tổng giá trị, NCC, điều khoản TT. 3\. Xem file PDF IPO đã ký (nếu có). 4\. Chọn Phê duyệt → Xác nhận. 5\. IPO → Đã duyệt. Thông báo gửi Trưởng phòng mua hàng. |
| **Luồng — Từ chối** | 4a. Chọn Từ chối → Nhập lý do → Xác nhận. 5a. IPO → Từ chối. Thông báo kèm lý do gửi phòng mua hàng. 6a. Phòng mua hàng chỉnh sửa IPO và submit lại. |
| **Tham chiếu FR** | FR-05.2 |

### **UC-14 — Thực hiện mua hàng sau duyệt**

| Mã Use-Case | UC-14 |
| :---- | :---- |
| **Tên** | Thực hiện mua hàng sau khi IPO được duyệt |
| **Actor chính** | Trưởng phòng mua hàng |
| **Mô tả** | Sau khi IPO duyệt, trưởng phòng mua hàng liên hệ NCC và cập nhật trạng thái IPO để theo dõi tiến độ. |
| **Pre-condition** | IPO trạng thái Đã duyệt. |
| **Post-condition** | Trạng thái IPO cập nhật. NCC được liên hệ tiến hành giao hàng. |
| **Luồng chính** | 1\. Nhận thông báo IPO được duyệt. 2\. Liên hệ NCC xác nhận đơn hàng (ngoài hệ thống: email/điện thoại). 3\. Cập nhật trạng thái IPO: Đang thực hiện / Đã gửi đơn cho NCC. 4\. Theo dõi tiến độ giao hàng, cập nhật khi cần. |
| **Ghi chú** | Giai đoạn 1: không tự động gửi email đến NCC từ hệ thống sau khi IPO duyệt. Trưởng phòng MH liên hệ thủ công. |
| **Tham chiếu FR** | FR-05.3, FR-06 |

## **Module 7 — Cập nhật trạng thái đơn hàng**

### **UC-15 — Cập nhật trạng thái đơn hàng**

| Mã Use-Case | UC-15 |
| :---- | :---- |
| **Tên** | Cập nhật trạng thái đơn hàng |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Theo dõi và cập nhật trạng thái giao hàng của order sau khi IPO được duyệt. |
| **Pre-condition** | Order/IPO ở trạng thái Đã duyệt trở lên. |
| **Post-condition** | Trạng thái đơn cập nhật. Lịch sử ghi log với timestamp và người thực hiện. |
| **Luồng chính** | 1\. Mở danh sách order. 2\. Chọn order cần cập nhật. 3\. Chọn trạng thái mới: Chờ giao / Đang giao / Đã giao một phần / Đã giao đủ / Hủy. 4\. Nhập ghi chú (tùy chọn). 5\. Lưu. Hệ thống ghi log: trạng thái cũ → mới, thời gian, người cập nhật. |
| **Tham chiếu FR** | FR-06 |

## **Module 8 — Nhận hàng & Quản lý kho**

### **UC-16 — Nhập kho**

| Mã Use-Case | UC-16 |
| :---- | :---- |
| **Tên** | Nhập kho |
| **Actor chính** | Thủ kho |
| **Mô tả** | Xác nhận nhận hàng từ NCC, ghi nhận SL thực nhận và phân bổ hàng vào kho theo từng bộ phận đã request. |
| **Pre-condition** | Order trạng thái Đã giao một phần hoặc Đã giao đủ. Thủ kho đã đăng nhập. |
| **Post-condition** | Phiếu nhập kho được tạo. Trưởng bộ phận nhận thông báo hàng đến. |
| **Luồng chính** | 1\. Xem danh sách order chờ nhận hàng. 2\. Mở order, xem danh sách vật tư và bộ phận đã request. 3\. Nhập SL thực nhận cho từng vật tư (có thể nhận một phần — partial receipt). 4\. Nhập ghi chú nếu có sai lệch so với order. 5\. Xác nhận Nhập kho. Hệ thống tạo phiếu nhập kho. 6\. Thông báo gửi đến Trưởng bộ phận liên quan. |
| **Luồng ngoại lệ** | 3-E1. SL thực nhận \> SL đặt: cảnh báo, yêu cầu xác nhận. 3-E2. Nhận thiếu: ghi nhận số thiếu, order tiếp tục chờ giao phần còn lại. |
| **Tham chiếu FR** | FR-07.1 |

### **UC-17 — Xác nhận nhận hàng**

| Mã Use-Case | UC-17 |
| :---- | :---- |
| **Tên** | Xác nhận nhận hàng |
| **Actor chính** | Trưởng bộ phận |
| **Mô tả** | Xác nhận đã nhận hàng từ kho và đóng request tương ứng. |
| **Pre-condition** | Thủ kho đã xác nhận nhập kho và gửi thông báo. |
| **Post-condition** | PR tương ứng chuyển sang Đã nhận hàng (đóng). |
| **Luồng chính** | 1\. Nhận thông báo hàng đã vào kho. 2\. Xem chi tiết: vật tư, SL thực nhận. 3\. Tùy chọn: nhập đánh giá chất lượng hàng nhận. 4\. Xác nhận Đã nhận hàng. Hệ thống đóng PR liên quan. |
| **Tham chiếu FR** | FR-07.2 |

## **Module 9 — Hóa đơn & Thanh toán**

### **UC-18 — Nhập hóa đơn**

| Mã Use-Case | UC-18 |
| :---- | :---- |
| **Tên** | Nhập hóa đơn từ nhà cung cấp |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Upload file hóa đơn PDF hoặc nhập URL và liên kết với order. Một order có thể có nhiều hóa đơn. |
| **Pre-condition** | Order đã có ít nhất một lần nhập kho. |
| **Post-condition** | Hóa đơn lưu và liên kết với order \+ IPO. Sẵn sàng tạo yêu cầu thanh toán. |
| **Luồng chính** | 1\. Mở order. 2\. Chọn Thêm hóa đơn. 3a. Upload file PDF hóa đơn. 3b. Hoặc nhập URL link hóa đơn điện tử. 4\. Nhập thêm: số hóa đơn, ngày, tổng giá trị (tùy chọn). 5\. Lưu. Hệ thống liên kết hóa đơn với order và IPO. |
| **Tham chiếu FR** | FR-08.1 |

### **UC-19 — Tạo yêu cầu thanh toán**

| Mã Use-Case | UC-19 |
| :---- | :---- |
| **Tên** | Tạo yêu cầu thanh toán |
| **Actor chính** | Nhân viên mua hàng |
| **Mô tả** | Khi hóa đơn đã upload và IPO đã duyệt, tạo yêu cầu thanh toán gửi đến kế toán. |
| **Pre-condition** | Hóa đơn đã được upload. IPO trạng thái Đã duyệt. |
| **Post-condition** | Yêu cầu thanh toán được tạo. Kế toán nhận thông báo. |
| **Luồng chính** | 1\. Mở order. 2\. Kiểm tra: hóa đơn đã có, IPO đã duyệt. 3\. Chọn Tạo yêu cầu thanh toán. 4\. Điền: số tiền, hạn thanh toán, phương thức, ghi chú. 5\. Submit. Hệ thống gửi thông báo đến kế toán (in-app \+ email). |
| **Luồng ngoại lệ** | 2-E1. Hóa đơn chưa upload: nút tạo yêu cầu bị ẩn, hiển thị hướng dẫn. 2-E2. IPO chưa duyệt: không cho phép tạo yêu cầu. |
| **Tham chiếu FR** | FR-08.2 |

### **UC-20 — Xử lý thanh toán**

| Mã Use-Case | UC-20 |
| :---- | :---- |
| **Tên** | Xử lý thanh toán |
| **Actor chính** | Kế toán |
| **Mô tả** | Kế toán xem xét yêu cầu thanh toán, kiểm tra hóa đơn và dữ liệu order, thực hiện thanh toán và đóng invoice. |
| **Pre-condition** | Yêu cầu thanh toán tồn tại ở trạng thái Chờ xử lý. |
| **Post-condition** | Invoice được đóng. Dữ liệu lưu để kế toán nhập vào phần mềm kế toán nội bộ. |
| **Luồng chính** | 1\. Nhận thông báo yêu cầu thanh toán mới. 2\. Xem danh sách yêu cầu chờ xử lý. 3\. Mở yêu cầu, kiểm tra: hóa đơn, dữ liệu order, IPO đã duyệt. 4\. Thực hiện thanh toán thực tế bên ngoài hệ thống (chuyển khoản...). 5\. Quay lại hệ thống, nhập: ngày TT, số tham chiếu giao dịch, ghi chú. 6\. Đóng invoice. Trạng thái → Đã thanh toán. |
| **Luồng thay thế** | 6a. Trả hàng / hoàn tiền: ghi nhận Credit Note, liên kết với order và hóa đơn gốc. |
| **Ghi chú tích hợp** | Kế toán nhập thủ công vào phần mềm kế toán nội bộ dựa trên dữ liệu hệ thống. Không tích hợp tự động giai đoạn 1\. |
| **Tham chiếu FR** | FR-08.3 |

## **Module 10 — Báo cáo & Thống kê**

### **UC-21 — Xem báo cáo & thống kê**

| Mã Use-Case | UC-21 |
| :---- | :---- |
| **Tên** | Xem báo cáo và thống kê |
| **Actor chính** | Nhân viên/Trưởng phòng mua hàng, Giám đốc, Kế toán |
| **Mô tả** | Xem các báo cáo tổng hợp, lọc theo nhiều tiêu chí và xuất ra Excel/PDF. |
| **Pre-condition** | Actor đã đăng nhập và có quyền xem báo cáo tương ứng. |
| **Post-condition** | Báo cáo hiển thị trên màn hình. Có thể xuất file. |
| **Luồng chính** | 1\. Truy cập mục Báo cáo. 2\. Chọn loại báo cáo: Tình trạng PO / Hiệu suất NCC / Chi phí theo danh mục / Công nợ phải trả / Dashboard. 3\. Áp dụng bộ lọc: khoảng thời gian, bộ phận, NCC, danh mục. 4\. Hệ thống hiển thị dữ liệu dạng bảng và/hoặc biểu đồ. 5\. Xuất ra Excel hoặc PDF (tùy chọn). |
| **Phân quyền xem** | Giám đốc/Phó GĐ: tất cả báo cáo \+ Dashboard. Trưởng/NV mua hàng: Tình trạng PO, Hiệu suất NCC, Chi phí theo danh mục. Kế toán: Công nợ phải trả, Chi phí theo danh mục. |
| **Tham chiếu FR** | Mục 5 URD — Yêu cầu báo cáo & thống kê |

# **3\. Ma trận Actor × Use-Case**

Ký hiệu: ● Thực hiện chính   ○ Tham gia / được thông báo   — Không liên quan

| Mã | Tên Use-Case | T.BP | MH/TPM | GĐ/PGĐ | Kho | KT | NCC | Admin |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| UC-01 | Đăng nhập | ● | ● | ● | ● | ● | — | ● |
| UC-02 | Quản lý danh mục vật tư | — | ● | — | — | — | — | ● |
| UC-03 | Quản lý nhà cung cấp | — | ● | — | — | — | — | ● |
| UC-04 | Quản lý người dùng & PQ | — | — | — | — | — | — | ● |
| UC-05 | Tạo yêu cầu mua hàng (PR) | ● | ○ | — | — | — | — | — |
| UC-06 | Chỉnh sửa / Hủy PR | ● | ○ | — | — | — | — | — |
| UC-07 | Tạo giỏ hàng (Cart) | — | ● | — | — | — | — | — |
| UC-08 | Chỉnh sửa Cart | ○ | ● | — | — | — | — | — |
| UC-09 | Tạo Order & chọn NCC | — | ● | — | — | — | — | — |
| UC-10 | Gửi yêu cầu báo giá | — | ● | — | — | — | ○ | — |
| UC-11 | Nhập báo giá | — | ○ | — | — | — | ● | — |
| UC-12 | So sánh & chốt / Xuất IPO | — | ● | — | — | — | — | — |
| UC-13 | Phê duyệt IPO | — | ○ | ● | — | — | — | — |
| UC-14 | Thực hiện MH sau duyệt | — | ● | ○ | — | — | — | — |
| UC-15 | Cập nhật trạng thái đơn | — | ● | — | — | — | — | — |
| UC-16 | Nhập kho | ○ | — | — | ● | — | — | — |
| UC-17 | Xác nhận nhận hàng | ● | — | — | ○ | — | — | — |
| UC-18 | Nhập hóa đơn | — | ● | — | — | — | — | — |
| UC-19 | Tạo yêu cầu thanh toán | — | ● | — | — | ○ | — | — |
| UC-20 | Xử lý thanh toán | — | — | — | — | ● | — | — |
| UC-21 | Xem báo cáo & thống kê | — | ● | ● | — | ● | — | — |

*Ghi chú: T.BP \= Trưởng bộ phận  |  MH/TPM \= Nhân viên & Trưởng phòng mua hàng  |  GĐ/PGĐ \= Giám đốc / Phó GĐ  |  KT \= Kế toán  |  NCC \= Nhà cung cấp  |  Admin \= Quản trị viên*

# **4\. Phụ lục**

## **4.1 Bảng trạng thái đối tượng**

Trạng thái PR (Purchase Requisition):

| Trạng thái | Điều kiện vào | Chuyển tiếp sang |
| :---- | :---- | :---- |
| Chờ xử lý | PR vừa được tạo | Đã vào cart / Đã hủy |
| Đã vào cart | PR được thêm vào cart | Đang xử lý / Chờ xử lý (nếu bị bỏ khỏi cart) |
| Đang xử lý | Order được tạo từ cart chứa PR này | Đã nhận hàng |
| Đã nhận hàng | Trưởng bộ phận xác nhận nhận | — (kết thúc) |
| Đã hủy | Người tạo hoặc mua hàng hủy | — (kết thúc) |

Trạng thái IPO:

| Trạng thái | Điều kiện vào | Chuyển tiếp sang |
| :---- | :---- | :---- |
| Draft | Sau khi chốt giá và xuất IPO | Chờ duyệt / Draft (nếu chỉnh sửa) |
| Chờ duyệt | Submit duyệt từ phòng mua hàng | Đã duyệt / Từ chối |
| Đã duyệt | Giám đốc phê duyệt | Đang thực hiện |
| Từ chối | Giám đốc từ chối | Draft (chỉnh sửa lại) |
| Đang thực hiện | Trưởng phòng MH xác nhận liên hệ NCC | Hoàn tất |

## **4.2 Thay đổi so với URD v1.0**

| Mục | Nội dung cũ | Nội dung mới | Tác động |
| :---- | :---- | :---- | :---- |
| 7.5 — Hạ tầng | On-premise | Cloud | Xem xét lại yêu cầu bảo mật dữ liệu, SLA, backup policy, lưu trữ trong/ngoài VN. |
| 8.1 — Database | MySQL | SQL Server | Cập nhật ORM/driver trong Python Flask/Django. Kiểm tra license SQL Server. |
| FR-05.2 — IPO duyệt | Tự động gửi email NCC | Thông báo phòng MH liên hệ NCC | Bổ sung UC-14. Không tự động gửi email NCC từ hệ thống sau duyệt. |

*— Hết tài liệu —*