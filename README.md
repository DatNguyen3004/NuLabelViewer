# NuLabel Viewer - Hệ thống kiểm định dữ liệu Xe tự hành

## 📌 Giới thiệu
Dự án NuLabel Viewer giúp quản lý và kiểm định nhãn dữ liệu từ tập dữ liệu nuScenes. 
Hỗ trợ hiển thị 6 camera đồng bộ và quản lý lỗi dán nhãn thông qua SQL Server.

## 🚀 Tính năng chính
- **Dashboard:** Thống kê tổng quan dữ liệu.
- **Workspace:** Hiển thị 360 độ (6 camera), kiểm định nhãn (CRUD).
- **Error Management:** Quản lý và lọc danh sách lỗi dán nhãn.

## 🛠 Cài đặt & Chạy dự án
1. **Yêu cầu:** Python 3.x, SQL Server.
2. **Cài đặt thư viện:** `pip install -r requirements.txt`
3. **Cấu hình Database:** Chỉnh sửa thông tin kết nối trong file `database.py`.
4. **Dataset:** Tải nuScenes dataset và đặt vào thư mục `/data`.
5. **Chạy ứng dụng:** `python app.py`

## 📸 Giao diện (Screenshots)
![Dashboard](path_to_your_image)
![Workspace](path_to_your_image)