

**USER REQUIREMENTS DOCUMENT**

**Hệ thống Quản lý Mua hàng**

Doanh nghiệp Sản xuất

| Phiên bản: | 1.0 |
| :---- | :---- |
| **Ngày lập:** | 23/03/2026 |
| **Trạng thái:** | Draft — chờ xác nhận khách hàng |
| **Thời gian dự kiến:** | 2 tháng (28 ngày phát triển) |

# **1\. Tổng quan dự án**

## **1.1 Giới thiệu**

Tài liệu này mô tả các yêu cầu người dùng (User Requirements) cho hệ thống quản lý mua hàng của doanh nghiệp sản xuất. Nội dung được tổng hợp từ kết quả khảo sát nghiệp vụ và buổi trao đổi với đại diện khách hàng.

Hệ thống hướng đến mục tiêu số hóa toàn bộ quy trình mua hàng — từ khi phát sinh nhu cầu mua tại các phòng ban, qua bước lập yêu cầu, phê duyệt, thu thập báo giá, phát hành đơn đặt hàng (IPO/PO), nhận hàng vào kho, cho đến thanh toán cho nhà cung cấp — thay thế các công cụ thủ công hiện tại (email, Excel).

## **1.2 Mục tiêu hệ thống**

* Chuẩn hóa và tự động hóa quy trình mua hàng từ đầu đến cuối

* Đảm bảo minh bạch thông tin giữa các bộ phận: Sản xuất, Mua hàng, Kho, Kế toán, Ban giám đốc

* Hỗ trợ phê duyệt đa cấp theo phân quyền vai trò (RBAC)

* Tự động gửi yêu cầu báo giá đến nhà cung cấp qua email kèm link nhập báo giá

* Xuất IPO (Internal Purchase Order) dạng PDF để ký, scan và upload

* Quản lý trạng thái đơn hàng, nhận hàng vào kho và yêu cầu thanh toán

* Nền tảng sẵn sàng mở rộng tích hợp ERP/kế toán trong tương lai

## **1.3 Phạm vi dự án**

Hệ thống bao gồm các module chính sau:

* Module quản lý danh mục (Master Data): vật tư, nhà cung cấp, người dùng

* Module yêu cầu mua hàng (Purchase Requisition)

* Module giỏ hàng & lập đơn mua (Cart & Order)

* Module báo giá (Quotation) — bao gồm cổng nhập báo giá cho nhà cung cấp

* Module phê duyệt IPO

* Module nhận hàng & quản lý kho

* Module hóa đơn & thanh toán

* Module báo cáo & thống kê

Ngoài phạm vi (Not In Scope — giai đoạn 1):

* Tích hợp trực tiếp với phần mềm kế toán (MISA, Fast, SAP...)

* Cổng nhà cung cấp (Vendor Portal) tự phục vụ đầy đủ

* Module tính định mức vật tư tự động (BOM-based MRP)

* Tích hợp hệ thống WMS, MES, QMS

## **1.4 Các bên liên quan (Stakeholders)**

| Vai trò | Bộ phận | Trách nhiệm trong hệ thống |
| :---- | :---- | :---- |
| Trưởng bộ phận sản xuất | Sản xuất | Tạo yêu cầu mua hàng, xác nhận nhận hàng |
| Nhân viên mua hàng | Phòng mua hàng | Lập cart, tạo order, gửi yêu cầu báo giá, quản lý IPO |
| Nhà cung cấp (Supplier) | Bên ngoài | Nhập báo giá qua link được cấp |
| Giám đốc / Phó giám đốc | Ban giám đốc | Phê duyệt IPO, xem báo cáo tổng hợp |
| Thủ kho | Kho | Nhập hàng vào kho theo order đã duyệt |
| Kế toán | Kế toán | Xác nhận hóa đơn, thực hiện thanh toán |

## **1.5 Thông tin kỹ thuật triển khai**

| Hạng mục | Thông tin |
| :---- | :---- |
| Nền tảng backend | Python (Flask hoặc Django) |
| Cơ sở dữ liệu | MySQL |
| Môi trường triển khai | On-premise |
| Xác thực | Đăng nhập bằng email, mật khẩu mã hóa bcrypt |
| Bảo mật | Phân quyền RBAC theo vai trò |
| Tích hợp hiện tại | Không (độc lập, kế toán nhập thủ công) |
| Thời gian hoàn thành | 2 tháng (28 ngày phát triển thực) |

# **2\. Quy trình nghiệp vụ tổng thể**

Quy trình mua hàng được chia thành 6 giai đoạn chính, thực hiện tuần tự:

| Bước | Giai đoạn | Mô tả | Người thực hiện |
| :---- | :---- | :---- | :---- |
| 1 | Yêu cầu mua hàng | Trưởng bộ phận tạo PR cho vật tư cần mua | Trưởng bộ phận |
| 2 | Lập giỏ hàng & đơn mua | Phòng mua hàng gom các PR, tạo cart và order theo nhóm vật tư | Nhân viên mua hàng |
| 3 | Thu thập báo giá | Gửi yêu cầu báo giá đến nhà cung cấp; NCC nhập giá qua link riêng | Mua hàng \+ NCC |
| 4 | Phê duyệt IPO | Phòng mua hàng chốt giá, xuất IPO PDF; Giám đốc phê duyệt | Mua hàng \+ GĐ |
| 5 | Nhận hàng & vào kho | Kho nhận hàng theo order; trưởng bộ phận xác nhận nhận | Kho \+ bộ phận |
| 6 | Hóa đơn & thanh toán | Upload hóa đơn, yêu cầu thanh toán, kế toán xử lý và đóng invoice | Mua hàng \+ KT |

## **2.1 Luồng xử lý chi tiết**

Ghi chú từ buổi khảo sát:

* Nhiều phòng ban có thể cùng request 1 loại vật tư trong cùng kỳ (ví dụ: giấy in). Phòng mua hàng sẽ gom các request này vào 1 cart để mua gộp, giảm chi phí.

* Báo giá của nhà cung cấp được bảo mật — chỉ người có thẩm quyền mới xem được nội dung báo giá.

* Nhà cung cấp có thể được phép cập nhật báo giá nhiều lần trước deadline, miễn là đơn hàng chưa chốt.

* IPO sau khi xuất PDF sẽ được in, ký tay, scan và upload lại vào hệ thống.

* Kế toán không tích hợp tự động — họ sẽ nhập thủ công vào phần mềm kế toán dựa trên dữ liệu trên hệ thống.

* Hệ thống cần được thiết kế linh hoạt để dễ dàng thay đổi workflow trong tương lai.

# **3\. Yêu cầu chức năng (Functional Requirements)**

## **FR-01: Quản lý danh mục (Master Data)**

### **FR-01.1 Danh mục vật tư / sản phẩm**

Hệ thống phải cho phép quản lý danh sách vật tư chuẩn (master list) bao gồm:

* Mã vật tư, tên, mô tả, đơn vị tính (kg, chiếc, lít, bộ...)

* Nhóm danh mục (nguyên vật liệu, bao bì, vật tư tiêu hao, thiết bị, dịch vụ...)

* Trạng thái: đang hoạt động / ngừng sử dụng

* Hỗ trợ tìm kiếm nhanh theo tên hoặc mã khi tạo yêu cầu mua

* Cho phép nhập free text (loại "Other") khi vật tư chưa có trong danh mục

### **FR-01.2 Danh mục nhà cung cấp**

Hệ thống phải lưu trữ thông tin nhà cung cấp bao gồm:

* Tên công ty, địa chỉ, mã số thuế

* Người liên lạc, email, số điện thoại (có thể có nhiều liên lạc)

* Nhóm hàng cung cấp

* Trạng thái: đang hoạt động / tạm dừng

* Điều khoản thanh toán mặc định

* Chức năng thêm mới, chỉnh sửa, tìm kiếm nhà cung cấp

### **FR-01.3 Quản lý người dùng & phân quyền**

Hệ thống sử dụng mô hình RBAC với các vai trò sau:

| Vai trò | Quyền hạn |
| :---- | :---- |
| Giám đốc | Xem tất cả, phê duyệt IPO, xem toàn bộ báo cáo |
| Phó giám đốc | Tương tự giám đốc (hoặc giới hạn theo cấu hình) |
| Trưởng phòng mua hàng | Quản lý cart, order, báo giá, IPO; xuất báo cáo |
| Nhân viên mua hàng | Tạo cart, order; gửi báo giá; cập nhật trạng thái |
| Trưởng bộ phận sản xuất | Tạo / xem request của bộ phận mình; xác nhận nhận hàng |
| Thủ kho | Nhập kho theo order; xem danh sách hàng cần nhận |
| Kế toán | Xem hóa đơn, xử lý thanh toán, đóng invoice |

* Mỗi người dùng thuộc về một bộ phận/chi nhánh

* Quản trị viên có thể thêm/sửa/vô hiệu hóa tài khoản

* Đăng nhập bằng email \+ mật khẩu (bcrypt)

## **FR-02: Yêu cầu mua hàng (Purchase Requisition — PR)**

### **FR-02.1 Tạo yêu cầu mua hàng**

Người thực hiện: Trưởng bộ phận sản xuất

* Tìm kiếm và chọn vật tư từ danh mục master (hỗ trợ autocomplete)

* Nhập số lượng cần mua và đơn vị tính

* Chọn hoặc nhập thêm loại vật tư không có trong danh mục (free text "Other")

* Nhập thông tin bổ sung: độ ưu tiên (thường / khẩn), thời hạn cần hàng, ghi chú

* Hệ thống tự động ghi nhận bộ phận, người tạo, ngày tạo

* Trạng thái ban đầu: Chờ phê duyệt

### **FR-02.2 Chỉnh sửa và hủy yêu cầu**

* Người tạo có thể chỉnh sửa PR khi trạng thái còn Chờ phê duyệt

* Hệ thống lưu lịch sử thay đổi (ai sửa, sửa gì, lúc nào)

* Khi sửa hoặc hủy, hệ thống gửi thông báo đến phòng mua hàng

* Khi phòng mua hàng đã chỉnh sửa PR trong cart, hệ thống thông báo lại cho người tạo PR

### **FR-02.3 Trạng thái PR**

| Trạng thái | Mô tả |
| :---- | :---- |
| Chờ phê duyệt | PR vừa được tạo, chưa được đưa vào cart |
| Đã vào cart | PR được phòng mua hàng chọn vào cart |
| Đang xử lý | Order đã được tạo từ cart chứa PR này |
| Đã nhận hàng | Bộ phận xác nhận đã nhận đủ hàng |
| Đã hủy | PR bị hủy bởi người tạo hoặc mua hàng |

## **FR-03: Giỏ hàng & Lập đơn mua (Cart & Order)**

### **FR-03.1 Quản lý giỏ hàng (Cart)**

Người thực hiện: Nhân viên mua hàng

* Lọc danh sách PR theo: danh mục vật tư, tên vật tư, ngày tạo, bộ phận, trạng thái, độ ưu tiên

* Chọn nhiều PR cùng lúc để đưa vào cart

* Mỗi cart có tiêu đề (title) để phân biệt; có thể có nhiều cart đang mở cùng lúc

* Trong cart: thêm / bớt PR; chỉnh sửa số lượng hoặc tên vật tư khi cần

* Lịch sử thay đổi cart được lưu lại; thông báo đến người tạo PR khi có thay đổi

### **FR-03.2 Tạo đơn mua (Order)**

* Với mỗi loại vật tư trong cart, hệ thống tổng hợp tổng số lượng yêu cầu từ tất cả PR

* Nhân viên mua hàng chọn danh sách nhà cung cấp sẽ gửi yêu cầu báo giá

* Thông tin liên hệ NCC (tên, email...) có thể tùy chỉnh trực tiếp khi tạo order

* Sau khi hoàn tất cấu hình, xác nhận và tạo order — hệ thống lưu đầy đủ thông tin

* Có thể tạo nhiều order từ cùng một cart (ví dụ: tách theo nhóm hàng, theo NCC)

### **FR-03.3 Chỉnh sửa đơn mua**

* Cho phép thêm nhà cung cấp vào order sau khi tạo

* Chỉnh sửa thông tin liên hệ NCC trong order

* Khi thay đổi số lượng, hệ thống thông báo cho các bên liên quan

* Khuyến nghị: thực hiện thay đổi số lượng từ cấp PR/Cart rồi cập nhật ngược lên order

## **FR-04: Thu thập báo giá (Quotation)**

### **FR-04.1 Gửi yêu cầu báo giá**

Người thực hiện: Nhân viên mua hàng

* Tạo email theo template sẵn có, đính kèm link báo giá riêng cho từng NCC

* Link báo giá được tự động sinh ra khi gửi email

* Có nút sinh link thủ công để mua hàng tự nhập báo giá thay NCC nếu cần

* Có thể đặt deadline báo giá; sau deadline NCC không thể cập nhật thêm

### **FR-04.2 Nhập báo giá (dành cho Nhà cung cấp)**

Người thực hiện: Nhà cung cấp (qua link, không cần tài khoản)

* NCC mở link và xem danh sách sản phẩm cần báo giá

* Form tối thiểu: tên sản phẩm, số lượng, đơn giá, tổng tiền, ghi chú

* Hỗ trợ nhập qua form web và có thể upload file Excel danh sách báo giá (do số lượng items có thể lớn)

* Sau khi submit, NCC nhận xác nhận; nếu còn trong deadline và order chưa chốt, NCC được phép cập nhật lại

* Khi NCC submit, hệ thống gửi thông báo cho phòng mua hàng

* Nội dung báo giá được bảo mật — chỉ người có thẩm quyền mới xem được

### **FR-04.3 Xem và so sánh báo giá**

* Phòng mua hàng xem báo giá của tất cả NCC trên cùng màn hình

* Hiển thị dạng bảng so sánh giá theo từng vật tư

* Có thể chốt từng mặt hàng riêng lẻ (không cần chốt toàn bộ order cùng lúc)

## **FR-05: Phê duyệt IPO (Internal Purchase Order)**

### **FR-05.1 Tạo và xuất IPO**

Người thực hiện: Nhân viên mua hàng

* Sau khi chốt giá, hệ thống tổng hợp thành bảng IPO gồm: tên sản phẩm, số lượng, đơn giá, tổng tiền, nhà cung cấp, điều khoản thanh toán

* Xuất IPO dạng PDF để in, ký tay, scan và upload lại vào hệ thống

* Có chức năng chỉnh sửa IPO trước khi submit phê duyệt (lưu lịch sử thay đổi)

### **FR-05.2 Phê duyệt IPO**

Người thực hiện: Giám đốc / Phó giám đốc

* Nhận thông báo khi có IPO chờ duyệt

* Xem chi tiết IPO bao gồm thông tin order, danh sách items, tổng giá trị

* Thao tác: Phê duyệt → hệ thống Thông báo tới phòng mua hàng để xử lý

* Thao tác: Từ chối \+ ghi lý do → phòng mua hàng nhận thông báo để xử lý lại

### **FR-05.3 Thực hiện IPO**

Người thực hiện: Trưởng Phòng mua hàng

* Nhận thông báo khi có IPO được phê duyệt

* Liên hệ với nhà cung cấp đề tiến hành mua hàng

* Thao tác: Cập nhật trạng thái của IPO

### **FR-05.4 Trạng thái IPO**

| Trạng thái | Mô tả |
| :---- | :---- |
| Draft | IPO đang được chuẩn bị, chưa submit duyệt |
| Chờ duyệt | Đã submit, chờ giám đốc phê duyệt |
| Đã duyệt | Giám đốc đã phê duyệt; đã gửi order cho NCC |
| Từ chối | Giám đốc từ chối; trả về phòng mua hàng |
| Đã chỉnh sửa | IPO đã được cập nhật sau phê duyệt (nếu cần) |

## **FR-06: Cập nhật trạng thái đơn hàng**

* Phòng mua hàng có thể cập nhật trạng thái giao hàng: Chờ giao / Đang giao / Đã giao một phần / Đã giao đủ / Hủy

* Có thể nhập ghi chú khi cập nhật trạng thái

* Lịch sử thay đổi trạng thái được lưu lại với thông tin người cập nhật và thời gian

## **FR-07: Nhận hàng & Quản lý kho**

### **FR-07.1 Nhập kho**

Người thực hiện: Thủ kho

* Xem danh sách order đang chờ nhận hàng

* Dựa vào thông tin order, xác nhận nhập kho cho từng sản phẩm theo từng phòng ban đã request

* Có thể nhận một phần (partial receipt) nếu hàng giao chưa đủ

* Nhập số lượng thực nhận; ghi chú nếu có sai lệch

### **FR-07.2 Xác nhận nhận hàng**

Người thực hiện: Trưởng bộ phận

* Nhận thông báo khi hàng đã được nhập kho cho bộ phận

* Xác nhận đã nhận hàng và đóng request tương ứng

* Có thể ghi chú đánh giá chất lượng hàng nhận (tùy chọn)

## **FR-08: Hóa đơn & Thanh toán**

### **FR-08.1 Nhập hóa đơn**

Người thực hiện: Nhân viên mua hàng

* Upload file PDF hóa đơn (hoặc nhập URL) cho một đơn hàng

* Liên kết hóa đơn với order và IPO tương ứng

* Hệ thống cho phép đính kèm nhiều hóa đơn cho một order (trường hợp giao nhiều lần)

### **FR-08.2 Yêu cầu thanh toán**

Người thực hiện: Nhân viên mua hàng

* Khi hóa đơn đã upload và IPO đã được duyệt, tạo yêu cầu thanh toán

* Điền thông tin: số tiền, hạn thanh toán, phương thức thanh toán, ghi chú

* Gửi thông báo đến kế toán

### **FR-08.3 Xử lý thanh toán**

Người thực hiện: Kế toán

* Xem danh sách yêu cầu thanh toán chờ xử lý

* Kiểm tra thông tin hóa đơn và dữ liệu order

* Nhập thông tin thanh toán thực tế: ngày thanh toán, số tham chiếu, ghi chú

* Đóng invoice sau khi hoàn tất thanh toán

* Hỗ trợ trường hợp trả hàng / hoàn tiền (ghi nhận Credit Note)

# **4\. Yêu cầu thông báo (Notification)**

Hệ thống phải gửi thông báo (in-app và/hoặc email) trong các tình huống sau:

| Sự kiện | Gửi đến | Kênh |
| :---- | :---- | :---- |
| PR mới được tạo | Phòng mua hàng | In-app \+ Email |
| PR bị sửa hoặc hủy | Phòng mua hàng | In-app \+ Email |
| PR trong cart bị mua hàng chỉnh sửa | Người tạo PR | In-app \+ Email |
| Yêu cầu báo giá được gửi | Nhà cung cấp | Email |
| NCC đã submit báo giá | Phòng mua hàng | In-app \+ Email |
| IPO chờ phê duyệt | Giám đốc / Phó GĐ | In-app \+ Email |
| IPO được duyệt / từ chối | Phòng mua hàng | In-app \+ Email |
| Order đã duyệt, gửi NCC | Nhà cung cấp | Email |
| Hàng đã nhập kho | Trưởng bộ phận liên quan | In-app \+ Email |
| Yêu cầu thanh toán mới | Kế toán | In-app \+ Email |

# **5\. Yêu cầu báo cáo & thống kê**

Hệ thống phải cung cấp các báo cáo sau:

| Tên báo cáo | Nội dung chính | Người xem |
| :---- | :---- | :---- |
| Tình trạng PO | Danh sách order theo trạng thái, NCC, thời gian | Mua hàng, GĐ |
| Hiệu suất nhà cung cấp | Tỷ lệ giao đúng hạn, số lần từ chối, lịch sử giá | Mua hàng, GĐ |
| Chi phí mua theo danh mục | Tổng chi theo nhóm vật tư, theo tháng/quý | Mua hàng, GĐ, KT |
| Công nợ phải trả | Hóa đơn chưa thanh toán, sắp đến hạn | Kế toán, GĐ |
| Dashboard tổng hợp | KPI mua hàng: số PR, số PO, tổng giá trị, trạng thái | Giám đốc |

Yêu cầu kỹ thuật báo cáo:

* Hỗ trợ lọc theo khoảng thời gian, bộ phận, nhà cung cấp, danh mục

* Xuất báo cáo ra Excel hoặc PDF

# **6\. Yêu cầu phi chức năng (Non-Functional Requirements)**

| Hạng mục | Yêu cầu |
| :---- | :---- |
| Bảo mật | Mật khẩu mã hóa bcrypt; phân quyền RBAC chặt chẽ; link báo giá NCC có token duy nhất và có hạn |
| Khả năng mở rộng | Kiến trúc modular, dễ thêm module mới (WMS, MRP, ERP) mà không cần refactor lớn |
| Linh hoạt workflow | Cấu hình quy trình duyệt (số cấp, ngưỡng giá trị) có thể thay đổi mà không cần sửa code |
| Khả dụng | Hệ thống hoạt động ổn định trong giờ hành chính; backup dữ liệu định kỳ |
| Hiệu năng | Thời gian phản hồi \< 3 giây cho thao tác thông thường; hỗ trợ upload file PDF hóa đơn và Excel báo giá |
| Tính khả dụng dữ liệu | Audit log đầy đủ: lịch sử thay đổi PR, order, IPO, thanh toán |
| Triển khai | On-premise; không lưu dữ liệu trên cloud nước ngoài |

# **7\. Ước tính chức năng & thời gian phát triển**

Tổng thời gian ước tính: 28 ngày phát triển thực (không tính review, test, UAT).

| STT | Màn hình / Tính năng | Người dùng | Mô tả chính | Ngày |
| :---- | :---- | :---- | :---- | :---- |
| 1 | Đăng ký Request | Trưởng bộ phận | Tìm vật tư trong master, nhập SL, đơn vị, ưu tiên, hạn | 2.5 |
| 2 | Chỉnh sửa / Hủy Request | Trưởng bộ phận | Thay đổi, hủy request; lịch sử thay đổi; notify mua hàng | 1 |
| 3 | Đăng ký Cart | Phòng mua hàng | Lọc request, multi-select vào cart, phân biệt cart bằng title | 2 |
| 4 | Chỉnh sửa Cart | Phòng mua hàng | Thêm/bớt request; chỉnh SL, tên; lịch sử; notify bộ phận | 1 |
| 5 | Confirm Cart / Tạo Order | Phòng mua hàng | Tổng hợp SL theo vật tư, chọn NCC, lưu order | 3 |
| 6 | Chỉnh sửa Order | Phòng mua hàng | Thêm NCC, sửa liên lạc, sửa SL có notify | 1 |
| 7 | Confirm Order / Yêu cầu báo giá | Phòng mua hàng | Tạo email từ template, gửi kèm link báo giá riêng từng NCC | 3 |
| 8 | Nhập báo giá | Nhà cung cấp | Form web \+ upload Excel; cho phép edit trước deadline; notify | 3 |
| 9 | Confirm giá / Xuất IPO | Phòng mua hàng | Chốt từng item, tổng hợp IPO, xuất PDF để ký | 3 |
| 10 | Confirm IPO | Giám đốc | Phê duyệt / từ chối IPO; gửi order chính thức đến NCC | 1 |
| 11 | Cập nhật trạng thái đơn hàng | Mua hàng / NCC | Cập nhật trạng thái giao hàng theo thời gian | 1 |
| 12 | Nhập kho | Thủ kho | Nhận hàng từ order; nhập SL thực nhận vào kho từng bộ phận | 0.5 |
| 13 | Nhận hàng | Trưởng bộ phận | Xác nhận đã nhận, đóng request | 0.5 |
| 14 | Nhập hóa đơn | Phòng mua hàng | Upload PDF / nhập URL hóa đơn cho order | 1 |
| 15 | Chỉnh sửa IPO | Phòng mua hàng | Cập nhật bảng IPO, xuất PDF mới sau chỉnh sửa | 2 |
| 16 | Yêu cầu thanh toán | Phòng mua hàng | Submit yêu cầu thanh toán khi đủ điều kiện | 0.5 |
| 17 | Thanh toán | Kế toán | Xử lý thanh toán, nhập thông tin, đóng invoice | 2 |
| **TỔNG CỘNG** |  |  |  | **28** |

# **8\. Vấn đề cần làm rõ (Open Issues)**

Các điểm sau đây cần được xác nhận với khách hàng trước khi bắt đầu thiết kế chi tiết:

| \# | Vấn đề | Tác động | Trạng thái |
| :---- | :---- | :---- | :---- |
| 1 | Quy trình phê duyệt PR: trưởng bộ phận tự duyệt hay cần duyệt thêm cấp? | Thiết kế màn hình duyệt | Chờ xác nhận |
| 2 | Ngưỡng giá trị để phân cấp duyệt IPO (GĐ / PGĐ)? | Cấu hình workflow duyệt | Chờ xác nhận |
| 3 | Hàng nhận không đủ / không đạt: quy trình cụ thể (nhận một phần, từ chối, quarantine)? | Module nhận hàng | Chờ xác nhận |
| 4 | NCC báo giá nhiều lần trong deadline: giữ tất cả lịch sử hay chỉ bản cuối? | Module báo giá | Chờ xác nhận |
| 5 | Có cần theo dõi tồn kho sau khi nhập không, hay hệ thống chỉ ghi nhận việc nhận hàng? | Phạm vi module kho | Chờ xác nhận |
| 6 | Điều kiện thanh toán (Net 30/45/60): lấy từ master NCC hay nhập tay theo từng order? | Module thanh toán | Chờ xác nhận |
| 7 | Email gửi NCC: dùng mail server nội bộ hay dịch vụ SMTP bên ngoài? | Cấu hình hệ thống | Chờ xác nhận |

# **9\. Phụ lục — Nguồn dữ liệu khảo sát**

Tài liệu này được tổng hợp từ các nguồn sau:

* Bộ câu hỏi khảo sát nghiệp vụ: khao\_sat\_nghiep\_vu\_mua\_hang — answers.csv

* Danh sách chức năng ước tính: Estimation — He\_thong\_mua\_hang — Functions.csv

* File quy trình nghiệp vụ: Meeting\_Duc\_app\_mua\_ban\_vat\_tu.pptx

Tóm tắt các câu trả lời khảo sát quan trọng:

| Mã | Câu hỏi | Câu trả lời khách hàng |
| :---- | :---- | :---- |
| 1.3 | Khối lượng mua hàng / tháng | 50 – 500 đơn/yêu cầu |
| 1.4 | Số chi nhánh | 2 chi nhánh / nhà máy |
| 2.1 | Số nhà cung cấp hoạt động | \~50 nhà cung cấp |
| 4.1 | Tạo PO | Nhân viên mua hàng tạo thủ công |
| 4.3 | Gửi PO cho NCC | Gửi email |
| 5.3 | Kiểm tra chất lượng đầu vào (IQC) | Không nằm trong phạm vi hệ thống hiện tại |
| 6.3 | Tích hợp kế toán | Chưa cần tích hợp; kế toán nhập thủ công |
| 6.4 | Quản lý thuế GTGT | Không yêu cầu |
| 7.2 | Tích hợp hệ thống khác | Không yêu cầu giai đoạn 1 |
| 7.3 | Phân quyền | RBAC: GĐ, PGĐ, trưởng phòng, nhân viên các bộ phận |
| 7.5 | Hạ tầng | Cloud |
| 7.6 | Timeline | Hoàn thành toàn bộ trong 2 tháng |
| 8.1 | Công nghệ | Python Flask/Django, SQL Server |

*— Hết tài liệu —*