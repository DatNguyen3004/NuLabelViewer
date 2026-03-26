import json
import pyodbc
import math
from datetime import datetime

import os

conn_str = r'DRIVER={SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=NuLabel_DB;Trusted_Connection=yes;'

def get_base_path():
    if os.path.exists("config.json"):
        with open("config.json", 'r') as f:
            p = json.load(f).get("dataset_path", "")
            if p:
                if not p.endswith('\\') and not p.endswith('/'):
                    p += '\\'
                return p
    return r"D:\NuLabelViewer_Project\static\Dataset\v1.0-mini\v1.0-mini\\"

base_path = get_base_path()

def full_reload_data():
    try:
        print("--- BẮT ĐẦU NẠP DỮ LIỆU ---")
        with open(base_path + "scene.json", 'r') as f: scenes_raw = json.load(f)
        with open(base_path + "sample.json", 'r') as f: samples_raw = json.load(f)
        with open(base_path + "sample_data.json", 'r') as f: data_raw = json.load(f)
        with open(base_path + "ego_pose.json", 'r') as f: ego_raw = json.load(f)

        scene_map = {s['token']: {'name': s['name'], 'desc': s['description']} for s in scenes_raw}
        ego_map = {e['token']: e for e in ego_raw}
        
        # --- THAY THẾ TOÀN BỘ LOGIC NẠP ẢNH VÀ TỌA ĐỘ XE ---
        mapping = {}
        sample_to_ego = {}
        
        print("Đang quét dữ liệu ảnh và tọa độ...")
        for d in data_raw:
            # Chỉ lấy ảnh Keyframe chuẩn
            if d.get('fileformat') == 'jpg' and d.get('is_key_frame') == True:
                t = d.get('sample_token')
                if t not in mapping: mapping[t] = {}
                
                fn = d.get('filename', '').upper()
                
                # Nạp đường dẫn ảnh chuẩn 6 camera
                if 'FRONT_LEFT' in fn: 
                    mapping[t]['FL'] = d['filename']
                elif 'FRONT_RIGHT' in fn: 
                    mapping[t]['FR'] = d['filename']
                elif 'BACK_LEFT' in fn: 
                    mapping[t]['BL'] = d['filename']
                elif 'BACK_RIGHT' in fn: 
                    mapping[t]['BR'] = d['filename']
                elif 'CAM_FRONT' in fn: 
                    mapping[t]['F'] = d['filename']
                    # QUAN TRỌNG: Lấy tọa độ xe tại đây để tính Speed
                    sample_to_ego[t] = ego_map.get(d.get('ego_pose_token'))
                elif 'CAM_BACK' in fn: 
                    mapping[t]['B'] = d['filename']

        print(f"-> Đã tìm thấy đường dẫn ảnh cho {len(mapping)} bộ.")
        print(f"-> Đã khớp được tọa độ xe cho {len(sample_to_ego)} bộ.")

        # 3. Tính toán Speed
        samples_sorted = sorted(samples_raw, key=lambda x: x['timestamp'])
        final_meta = {}
        speed_count = 0

        for i in range(len(samples_sorted)):
            curr = samples_sorted[i]
            t = curr['token']
            sc_info = scene_map.get(curr['scene_token'], {})
            
            # Logic thời tiết
            desc = sc_info.get('desc', '').lower()
            weather = "Trời nắng"
            if 'rain' in desc: weather = "Trời mưa"
            elif 'night' in desc: weather = "Ban đêm"

            # Logic tốc độ
            speed = 0
            if i > 0:
                prev = samples_sorted[i-1]
                if curr['scene_token'] == prev['scene_token']:
                    p1, p2 = sample_to_ego.get(t), sample_to_ego.get(prev['token'])
                    if p1 and p2:
                        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(p1['translation'], p2['translation'])))
                        dt = (p1['timestamp'] - p2['timestamp']) / 1000000.0
                        if dt > 0: 
                            speed = round((dist / dt) * 3.6, 1)
                            if speed > 0: speed_count += 1

            final_meta[t] = {
                'name': sc_info.get('name', 'N/A'),
                'weather': weather,
                'time': datetime.fromtimestamp(curr['timestamp'] / 1000000),
                'speed': speed
            }
        
        print(f"-> Đã tính được tốc độ thực tế (>0) cho {speed_count} mẫu.")

        # 4. Đẩy vào SQL
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Annotations; DELETE FROM Scenes;")
        
        sql_insert = """
            INSERT INTO Scenes (SampleToken, SceneName, CaptureTime, Weather, Speed,
            ImgPath_Front, ImgPath_Back, ImgPath_FrontLeft, ImgPath_FrontRight, ImgPath_BackLeft, ImgPath_BackRight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for t, cams in mapping.items():
            m = final_meta.get(t, {})
            cursor.execute(sql_insert, (t, m.get('name'), m.get('time'), m.get('weather'), m.get('speed', 0),
                cams.get('F'), cams.get('B'), cams.get('FL'), cams.get('FR'), cams.get('BL'), cams.get('BR')))

        conn.commit()
        print(f"--- THÀNH CÔNG! Đã nạp {len(mapping)} bộ ảnh ---")
        conn.close()

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    full_reload_data()