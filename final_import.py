import json
import pyodbc

# Cấu hình kết nối - Bro hãy kiểm tra DATABASE đúng tên NuLabel_DB chưa nhé
conn_str = r'DRIVER={SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=NuLabel_DB;Trusted_Connection=yes;'

def full_reload_data():
    path = r"D:\NuLabelViewer_Project\static\Dataset\v1.0-mini\v1.0-mini\sample_data.json"
    
    # 1. Đọc dữ liệu từ JSON
    print("Đang đọc file JSON...")
    with open(path, 'r') as f:
        sample_data = json.load(f)

    # 2. Gom nhóm ảnh theo SampleToken
    mapping = {}
    print("Đang phân tích và gom nhóm ảnh...")
    for item in sample_data:
        if item.get('fileformat') == 'jpg':
            token = item.get('sample_token')
            filename = item.get('filename', '')
            
            if token not in mapping:
                mapping[token] = {}

            fn_upper = filename.upper()
            if 'FRONT_LEFT' in fn_upper: mapping[token]['FL'] = filename
            elif 'FRONT_RIGHT' in fn_upper: mapping[token]['FR'] = filename
            elif 'BACK_LEFT' in fn_upper: mapping[token]['BL'] = filename
            elif 'BACK_RIGHT' in fn_upper: mapping[token]['BR'] = filename
            elif 'CAM_FRONT' in fn_upper: mapping[token]['F'] = filename
            elif 'CAM_BACK' in fn_upper: mapping[token]['B'] = filename

    # 3. Kết nối SQL và thực thi
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # XÓA DỮ LIỆU CŨ (Để làm mới từ đầu)
        print("Đang dọn dẹp dữ liệu cũ trong bảng Scenes...")
        cursor.execute("DELETE FROM Scenes") 
        
        # NẠP DỮ LIỆU MỚI
        print(f"Bắt đầu nạp {len(mapping)} bộ ảnh mới...")
        
        sql_insert = """
            INSERT INTO Scenes (
                SampleToken, 
                imgpath_front, imgpath_back, 
                imgpath_frontleft, imgpath_frontright, 
                imgpath_backleft, imgpath_backright
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        for token, cams in mapping.items():
            cursor.execute(sql_insert, (
                token, 
                cams.get('F'), cams.get('B'), 
                cams.get('FL'), cams.get('FR'), 
                cams.get('BL'), cams.get('BR')
            ))

        conn.commit()
        print(f"--- THÀNH CÔNG! Đã nạp mới {len(mapping)} bộ ảnh vào SQL ---")

    except Exception as e:
        print(f"Lỗi rồi bro ơi: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    full_reload_data()