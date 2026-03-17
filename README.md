🛰️ NuLabel Viewer: Hệ thống Kiểm soát Chất lượng Dữ liệu Xe tự hành

1. Phân tích bài toán & Tổng quan dự án
- Trong kỷ nguyên của trí tuệ nhân tạo và xe tự hành, dữ liệu là "nhiên liệu" cốt lõi. Tuy nhiên, việc gán nhãn hàng triệu khung hình từ tập dữ liệu nuScenes luôn tồn tại sai số. NuLabel Viewer ra đời như một giải pháp Quality Control (QC) chuyên sâu, giúp các chuyên gia kiểm định lại độ chính xác của các nhãn vật thể trong không gian 3D thông qua giao diện 2D đồng bộ.
- Dự án không chỉ đơn thuần là một trình xem ảnh, mà là một hệ thống quản lý quy trình làm việc (Workflow Management) từ khâu dữ liệu thô đến khi nhãn được phê duyệt cuối cùng.

2. Giải pháp kỹ thuật & Tính năng cốt lõi
📺 Không gian làm việc 360 độ (Synchronized Workspace)
- Đây là "trái tim" của hệ thống. Thay vì xem từng ảnh riêng lẻ, NuLabel Viewer đồng bộ hóa 6 ống kính camera:
- Front, Back, Sides: Cung cấp cái nhìn toàn cảnh giúp Reviewer xác nhận vật thể không bị bỏ sót hoặc gán nhãn nhầm vị trí giữa các vùng giao thoa của camera.
- Data Mapping: Tự động truy vấn tọa độ nhãn từ SQL Server và ánh xạ lên đúng khung hình tương ứng.

⚖️ Quy trình kiểm định (CRUD & Verification)
- Hệ thống cung cấp một cơ chế phản hồi hai chiều:
- Reviewer: Có quyền phê duyệt (Approve) hoặc từ chối (Reject) các nhãn dán. Nếu nhãn sai, lỗi sẽ được đẩy vào danh sách quản lý lỗi kèm theo mô tả chi tiết.
- Labeler: Nhận thông tin phản hồi ngay lập tức để thực hiện sửa đổi (Update/Delete), tối ưu hóa thời gian làm việc.

📊 Dashboard & Quản trị (Analytics)
- Cung cấp cái nhìn toàn cảnh về dự án thông qua các biểu đồ thống kê:
- Theo dõi tiến độ tổng thể của Dataset.
- Phân tích biểu đồ lỗi (Error Distribution) để xác định các loại vật thể thường bị gán nhãn sai nhất (ví dụ: Pedestrian, Cyclist).

🔑 Tài khoản trải nghiệm (Demo Credentials)
- Hệ thống được thiết kế với cơ chế phân quyền Role-based Access Control (RBAC). Bro có thể sử dụng các tài khoản sau để kiểm tra luồng nghiệp vụ:
- Admin: admin/admin123
- Reviewer: reviewer_1/check123
- Labeler: labeler_1/work123

🛠️ Kiến trúc hệ thống (Technical Stack)
- Dự án được xây dựng trên mô hình MVC (Model-View-Controller) đảm bảo tính mở rộng:
- Backend: Flask Framework kết hợp với SQLAlchemy để quản lý các quan hệ phức tạp giữa Scenes, ObjectLabels và Annotations.
- Database: Microsoft SQL Server - Đảm bảo tính toàn vẹn dữ liệu và khả năng truy vấn khối lượng lớn nhãn vật thể.
- Giao diện: Tối ưu hóa trải nghiệm người dùng với Bootstrap 5 và hệ thống icon nhận diện thương hiệu riêng.

🚀 Hướng dẫn triển khai nhanh
1. Khởi tạo môi trường: ```bash pip install -r requirements.txt
2. Cấu hình liên kết: Đảm bảo chuỗi kết nối trong database.py đã trỏ đúng về instance SQL Server của bạn.
3. Cấu trúc dữ liệu: Đặt bộ dữ liệu nuScenes vào thư mục /data để hệ thống bắt đầu load meta-data.
4. Vận hành: Chạy python app.py và truy cập vào cổng 5000.