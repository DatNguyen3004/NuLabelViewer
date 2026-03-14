import pyodbc
import json
import os

# 1. Hàm kết nối (Để app.py không còn báo lỗi ImportError)
def get_db_connection():
    conn_str = (
        r'DRIVER={SQL Server};'
        r'SERVER=localhost\SQLEXPRESS;'
        r'DATABASE=NuLabel_DB;'
        r'Trusted_Connection=yes;'
    )
    return pyodbc.connect(conn_str)

# 2. Hàm nạp 404 dữ liệu (Để giải quyết vụ 8 bộ ảnh)
def import_full_samples():
    path = r"D:\NuLabelViewer_Project\static\Dataset\v1.0-mini\v1.0-mini\sample.json"
    
    if not os.path.exists(path):
        print("Lỗi: Không tìm thấy file sample.json!")
        return

    with open(path, 'r') as f:
        samples = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"Đang nạp {len(samples)} mẫu ảnh vào SQL...")
    for s in samples:
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM Scenes WHERE SampleToken = ?)
            INSERT INTO Scenes (SampleToken) VALUES (?)
        """, (s['token'], s['token']))
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM Scenes")
    print(f"Thành công! Database hiện có: {cursor.fetchone()[0]} bộ ảnh.")
    conn.close()

# 3. Khi chạy trực tiếp file database.py thì nó sẽ nạp dữ liệu
if __name__ == "__main__":
    import_full_samples()