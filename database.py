import pyodbc
import json
import os

def get_db_connection():
    conn_str = (
        r'DRIVER={SQL Server};'
        r'SERVER=localhost\SQLEXPRESS;'
        r'DATABASE=NuLabel_DB;'
        r'Trusted_Connection=yes;'
    )
    return pyodbc.connect(conn_str)

def import_full_samples():
    # Cần cả 2 file để vừa lấy mã Token, vừa lấy đường dẫn ảnh
    sample_path = r"D:\NuLabelViewer_Project\static\Dataset\v1.0-mini\v1.0-mini\sample.json"
    data_path = r"D:\NuLabelViewer_Project\static\Dataset\v1.0-mini\v1.0-mini\sample_data.json"
    
    if not os.path.exists(sample_path) or not os.path.exists(data_path):
        print("Lỗi: Thiếu file JSON trong Dataset!")
        return

    # Bước 1: Thu thập 404 mã Token chuẩn
    with open(sample_path, 'r') as f:
        samples = json.load(f)
    valid_tokens = {s['token'] for s in samples}

    # Bước 2: Quét sample_data để lấy đường dẫn 6 camera cho mỗi Token
    with open(data_path, 'r') as f:
        sample_data = json.load(f)
    
    mapping = {token: {} for token in valid_tokens}
    for item in sample_data:
        token = item.get('sample_token')
        if token in mapping and item.get('fileformat') == 'jpg':
            fn = item.get('filename', '').upper()
            if 'FRONT_LEFT' in fn: mapping[token]['FL'] = item['filename']
            elif 'FRONT_RIGHT' in fn: mapping[token]['FR'] = item['filename']
            elif 'BACK_LEFT' in fn: mapping[token]['BL'] = item['filename']
            elif 'BACK_RIGHT' in fn: mapping[token]['BR'] = item['filename']
            elif 'CAM_FRONT' in fn: mapping[token]['F'] = item['filename']
            elif 'CAM_BACK' in fn: mapping[token]['B'] = item['filename']

    # Bước 3: Đẩy vào SQL (Xóa cũ nạp mới để đảm bảo sạch dữ liệu)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Đang làm sạch và nạp lại 404 bộ mẫu đầy đủ đường dẫn...")
    cursor.execute("DELETE FROM Scenes") # Xóa dữ liệu cũ chỉ có mỗi Token
    
    sql_insert = """
        INSERT INTO Scenes (SampleToken, imgpath_front, imgpath_back, 
                          imgpath_frontleft, imgpath_frontright, 
                          imgpath_backleft, imgpath_backright)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    for token in valid_tokens:
        c = mapping[token]
        cursor.execute(sql_insert, (token, c.get('F'), c.get('B'), 
                                   c.get('FL'), c.get('FR'), 
                                   c.get('BL'), c.get('BR')))
    
    conn.commit()
    print(f"Thành công! Đã nạp {len(valid_tokens)} bộ ảnh có đầy đủ đường dẫn.")
    conn.close()

if __name__ == "__main__":
    import_full_samples()