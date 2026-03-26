from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from database import get_db_connection
import json
import os
import subprocess

CONFIG_FILE = 'config.json'

def get_dataset_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
            p = cfg.get('dataset_path', '')
            if p: return p
    return r"D:\NuLabelViewer_Project\static\Dataset\v1.0-mini\v1.0-mini"

def save_dataset_path(path):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'dataset_path': path}, f)

app = Flask(__name__)
app.secret_key = 'nulabel_secret_key' # Cần thiết để dùng Session

# DANH SÁCH 3 TÀI KHOẢN MẶC ĐỊNH
USERS = {
    "admin": {
        "password": "admin123", 
        "full_name": "Admin Manager", 
        "role": "Quản trị viên"
    },
    "labeler_1": {
        "password": "work123", 
        "full_name": "Nguyễn Văn Label", 
        "role": "Người gán nhãn"
    },
    "reviewer_1": {
        "password": "check123", 
        "full_name": "Trần Thị Kiểm Định", 
        "role": "Người kiểm duyệt"
    }
}

@app.route('/workspace')
@app.route('/workspace/<current_token>') # QUAN TRỌNG: Thêm dòng này để nhận token từ nút bấm
def workspace(current_token=None):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    if not conn:
        return "Lỗi kết nối Database!"
    
    cursor = conn.cursor()
    
    # 1. LẤY DANH SÁCH TẤT CẢ TOKEN (Sửa lỗi: Dùng SampleToken thay vì ID)
    cursor.execute("SELECT SampleToken FROM Scenes ORDER BY SampleToken")
    all_tokens = [row[0] for row in cursor.fetchall()]
    total_count = len(all_tokens)

    if total_count == 0:
        return "<h1>Hệ thống chưa có dữ liệu ảnh!</h1>"

    # 2. XÁC ĐỊNH TOKEN HIỆN TẠI
    if not current_token:
        # Tìm bộ ảnh CHƯA DUYỆT đầu tiên
        cursor.execute("""
            SELECT TOP 1 S.SampleToken FROM Scenes S
            LEFT JOIN Annotations A ON S.SampleToken = A.SampleToken
            WHERE A.SampleToken IS NULL
            ORDER BY S.SampleToken
        """)
        row_init = cursor.fetchone()
        current_token = row_init[0] if row_init else all_tokens[0]

    # 3. TÍNH TOÁN VỊ TRÍ (INDEX) VÀ ĐIỀU HƯỚNG
    try:
        curr_index = all_tokens.index(current_token)
    except ValueError:
        curr_index = 0
        current_token = all_tokens[0]

    prev_token = all_tokens[curr_index - 1] if curr_index > 0 else all_tokens[0]
    next_token = all_tokens[curr_index + 1] if curr_index < total_count - 1 else all_tokens[-1]

    # 4. LẤY DỮ LIỆU 6 CAM VÀ THÔNG TIN CHI TIẾT
    cursor.execute("SELECT * FROM Scenes WHERE SampleToken = ?", (current_token,))
    row = cursor.fetchone()
    
    if not row:
        return "<h1>Không tìm thấy dữ liệu cho Token này!</h1>"

    # 5. TÍNH TIẾN ĐỘ (%)
    cursor.execute("SELECT COUNT(*) FROM Annotations")
    labeled_count = cursor.fetchone()[0] or 0
    progress_pct = round((labeled_count / total_count) * 100, 1) if total_count > 0 else 0

    # 3. TÌM TOKEN ĐIỀU HƯỚNG
    curr_index = all_tokens.index(current_token)
    
    first_token = all_tokens[0]
    last_token  = all_tokens[-1]
    prev_token  = all_tokens[curr_index - 1] if curr_index > 0 else first_token
    next_token  = all_tokens[curr_index + 1] if curr_index < total_count - 1 else last_token
    
    # --- LOGIC XỬ LÝ ĐƯỜNG DẪN ẢNH ---
    prefix = "/dataset/"
    def fix_path(p):
        return prefix + p.replace('\\', '/').strip() if p else ""

    cams = {
        'front': fix_path(row[2]), 'back': fix_path(row[3]),
        'front_left': fix_path(row[4]), 'front_right': fix_path(row[5]),
        'back_left': fix_path(row[6]), 'back_right': fix_path(row[7])
    }

    # 6. THỐNG KÊ VẬT THỂ TRONG 6 CAM HIỆN TẠI
    cursor.execute("""
        SELECT Category, COUNT(*) 
        FROM ObjectLabels 
        WHERE SampleToken = ? 
        GROUP BY Category
    """, (current_token,))
    rows_objects = cursor.fetchall()

    object_summary = []
    total_in_scene = 0
    for r in rows_objects:
        count = r[1]
        total_in_scene += count
        object_summary.append({
            'name': r[0].split('.')[-1].upper(),
            'count': count
        })
    
    cursor.close()
    conn.close()

    return render_template('workspace.html', 
        token=current_token, cams=cams,
        prev_token=prev_token, next_token=next_token, # Chỉ cần 2 biến này
        curr_num=curr_index + 1, total_count=total_count,
        progress_pct=progress_pct, object_summary=object_summary,
        total_objects=total_in_scene)

@app.route('/verify', methods=['POST'])
def verify():
    token = request.form.get('sample_token')
    status = request.form.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. LƯU HOẶC CẬP NHẬT TRẠNG THÁI DUYỆT (Dùng logic MERGE đơn giản)
    # Kiểm tra xem đã tồn tại chưa
    cursor.execute("SELECT COUNT(*) FROM Annotations WHERE SampleToken = ?", (token,))
    exists = cursor.fetchone()[0]
        
    # 1. LƯU DỮ LIỆU (Giữ nguyên)
    cursor.execute("SELECT COUNT(*) FROM Annotations WHERE SampleToken = ?", (token,))
    if cursor.fetchone()[0]:
        cursor.execute("UPDATE Annotations SET ReviewStatus = ?, ReviewDate = GETDATE() WHERE SampleToken = ?", (int(status), token))
    else:
        cursor.execute("INSERT INTO Annotations (SampleToken, ReviewStatus, ReviewDate) VALUES (?, ?, GETDATE())", (token, int(status)))
    conn.commit()

    # 2. LOGIC NHẢY THÔNG MINH (SKIP NHỮNG THẰNG ĐÃ LÀM)
    # Tìm thằng chưa làm đầu tiên có Token "lớn hơn" thằng vừa làm (theo thứ tự sắp xếp)
    cursor.execute("""
        SELECT TOP 1 S.SampleToken FROM Scenes S
        LEFT JOIN Annotations A ON S.SampleToken = A.SampleToken
        WHERE A.SampleToken IS NULL AND S.SampleToken > ?
        ORDER BY S.SampleToken
    """, (token,))
    
    next_row = cursor.fetchone()
    
    if not next_row:
        # Nếu từ đây đến cuối không còn ai, quay lại tìm thằng chưa làm đầu tiên từ đầu danh sách (Smart Resume)
        cursor.execute("""
            SELECT TOP 1 S.SampleToken FROM Scenes S
            LEFT JOIN Annotations A ON S.SampleToken = A.SampleToken
            WHERE A.SampleToken IS NULL
            ORDER BY S.SampleToken
        """)
        next_row = cursor.fetchone()

    cursor.close()
    conn.close()

    if next_row:
        # Nhảy tới thằng chưa làm gần nhất (Ví dụ: nhảy từ 25 vèo sang 27 vì 26 xong rồi)
        return redirect(url_for('analytics', current_token=next_row[0]))
    else:
        # Nếu đã làm sạch sành sanh 404 bộ, báo hoàn thành hoặc về bộ cuối cùng
        return redirect(url_for('analytics', current_token=token))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Logic kiểm tra
        user = USERS.get(username)
        if user and user['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            # Gửi thông báo lỗi về trang Login
            flash("Tài khoản không tồn tại hoặc mật khẩu chưa đúng!", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard') # Cả 2 đường dẫn đều chạy chung 1 hàm bên dưới
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Lấy thông tin đầy đủ của user đang đăng nhập
    user_info = USERS.get(session.get('username'))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # BƯỚC 1: Định nghĩa hàm get_count trước (Phải nằm TRÊN đoạn sử dụng)
    def get_count(cat):
        cursor.execute("SELECT COUNT(*) FROM ObjectLabels WHERE Category = ?", (cat,))
        row = cursor.fetchone()
        return row[0] if row else 0
    
    # 1. Lấy số lượng từng loại (giữ nguyên)
    counts = {
        'cars': get_count('car'),
        'peds': get_count('pedestrian'),
        'trucks': get_count('truck'),
        'bikes': get_count('bicycle')
    }
    
    total = sum(counts.values()) # Biến total nằm ở đây

    # 2. Tính toán trực tiếp, không dùng hàm con để tránh lỗi Scope
    stats = {
        'cars': {
            'count': counts['cars'], 
            'pct': round((counts['cars'] / total * 100), 1) if total > 0 else 0
        },
        'peds': {
            'count': counts['peds'], 
            'pct': round((counts['peds'] / total * 100), 1) if total > 0 else 0
        },
        'trucks': {
            'count': counts['trucks'], 
            'pct': round((counts['trucks'] / total * 100), 1) if total > 0 else 0
        },
        'bikes': {
            'count': counts['bikes'], 
            'pct': round((counts['bikes'] / total * 100), 1) if total > 0 else 0
        }
    }
    
    # Lấy 5 hoạt động gần đây
    query_history = """
        SELECT TOP 5 
            S.SampleToken, -- Dùng tạm SampleToken vì không có SceneName
            A.SampleToken as TokenID, 
            A.ReviewStatus, 
            A.ReviewDate,
            ISNULL(DATEDIFF(MINUTE, A.ReviewDate, GETDATE()), 0) as DiffMinutes
        FROM Annotations A
        JOIN Scenes S ON A.SampleToken = S.SampleToken
        ORDER BY A.ReviewDate DESC
    """

    cursor.execute(query_history)
    history = cursor.fetchall()

    query_queue = """
        SELECT COUNT(*) 
        FROM Scenes 
        WHERE SampleToken NOT IN (SELECT SampleToken FROM Annotations)
    """
    cursor.execute(query_queue)
    queue_count = cursor.fetchone()[0] # Định nghĩa biến queue_count ở đây

    cursor.close()
    conn.close()
    
    # QUAN TRỌNG: Truyền đúng tên biến 'stats' vào HTML
    return render_template('dashboard.html',
                            user_info=user_info,
                            stats=stats,
                            history=history, 
                            queue=queue_count)

@app.route('/analytics')
@app.route('/analytics/<current_token>')
def analytics(current_token=None):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Lấy thông tin đầy đủ của user đang đăng nhập
    user_info = USERS.get(session.get('username'))
    conn = get_db_connection()
    if not conn: return "Lỗi kết nối Database!"
    cursor = conn.cursor()

    # --- 1. LẤY TẤT CẢ TOKEN ĐỂ TÍNH THỨ TỰ (4/404) ---
    cursor.execute("SELECT SampleToken FROM Scenes ORDER BY SampleToken")
    all_tokens = [row[0] for row in cursor.fetchall()]
    total_count = len(all_tokens)

    # 2. LOGIC TỰ ĐỘNG QUAY LẠI BỘ CHƯA LÀM (SMART RESUME)
    if not current_token:
        # Tìm SampleToken đầu tiên chưa có trong bảng Annotations
        cursor.execute("""
            SELECT TOP 1 S.SampleToken FROM Scenes S
            LEFT JOIN Annotations A ON S.SampleToken = A.SampleToken
            WHERE A.SampleToken IS NULL
            ORDER BY S.SampleToken
        """)
        row_pending = cursor.fetchone()

        if row_pending:
            current_token = row_pending[0]
        elif all_tokens:
            current_token = all_tokens[0] # Nếu đã làm hết thì mới lấy bộ 1

    # Tính Index và các nút điều hướng
    curr_num = 0
    prev_token = next_token = None
    if current_token:
        curr_index = all_tokens.index(current_token)
        curr_num = curr_index + 1
        prev_token = all_tokens[curr_index - 1] if curr_index > 0 else all_tokens[0]
        next_token = all_tokens[curr_index + 1] if curr_index < total_count - 1 else all_tokens[-1]

    # --- 2. TIẾN ĐỘ TỔNG DỰ ÁN ---
    cursor.execute("SELECT COUNT(*) FROM Annotations")
    labeled_scenes = cursor.fetchone()[0] or 0
    progress = {
        'total': total_count,
        'labeled': labeled_scenes,
        'pending': total_count - labeled_scenes,
        'pct': round((labeled_scenes / total_count * 100), 1) if total_count > 0 else 0
    }

    # --- 3. LẤY DỮ LIỆU CHI TIẾT CỦA SCENE ĐANG CHỌN ---
    cursor.execute("SELECT * FROM Scenes WHERE SampleToken = ?", (current_token,))
    row = cursor.fetchone()

    prefix = "/dataset/"
    def fix_path(p): return prefix + p.replace("\\", "/").strip() if p else ""

    cams = None
    scene_info = None
    object_summary = []
    total_scene_objects = 0

    if row:
        scene_info = {
            'name': row[8],
            'time': row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else "N/A",
            'weather': row[10],
            'speed': row[11]
        }
        cams = {
            "front": fix_path(row[2]), "back": fix_path(row[3]),
            "front_left": fix_path(row[4]), "front_right": fix_path(row[5]),
            "back_left": fix_path(row[6]), "back_right": fix_path(row[7])
        }
        # Đếm vật thể của riêng bộ này
        cursor.execute("SELECT Category, COUNT(*) FROM ObjectLabels WHERE SampleToken = ? GROUP BY Category ORDER BY COUNT(*) DESC", (current_token,))
        for r in cursor.fetchall():
            total_scene_objects += r[1]
            object_summary.append({'name': r[0].split('.')[-1].upper(), 'count': r[1]})

    # --- 4. THỐNG KÊ BIỂU ĐỒ & LỊCH SỬ (Toàn dự án) ---
    cursor.execute("SELECT ReviewStatus, COUNT(*) FROM Annotations GROUP BY ReviewStatus")
    status_stats = {str(r[0]): r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT TOP 10 SampleToken, ReviewStatus, ReviewDate FROM Annotations ORDER BY ReviewDate DESC")
    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('analytics.html',
        user_info=user_info,
        progress=progress,
        status_stats=status_stats,
        object_summary=object_summary,
        total_all_objects=total_scene_objects,
        history=history,
        cams=cams,
        scene_info=scene_info,
        token=current_token,     # Token hiện tại để gán vào Form Đúng/Sai
        curr_num=curr_num,       # Số "4"
        total_count=total_count, # Số "404"
        prev_token=prev_token,
        next_token=next_token
    )

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tìm kiếm theo SceneName hoặc SampleToken (dùng LIKE để tìm gần đúng)
    # Nếu bro muốn tìm chính xác thì bỏ dấu % đi
    cursor.execute("""
        SELECT TOP 1 SampleToken 
        FROM Scenes 
        WHERE SceneName LIKE ? OR SampleToken LIKE ?
    """, (f'%{query}%', f'%{query}%'))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Nếu thấy, nhảy vào trang Analytics của bộ đó luôn
        return redirect(url_for('analytics', current_token=row[0]))
    else:
        # Không thấy thì có thể về trang lỗi hoặc về Analytics mặc định
        return redirect(url_for('analytics'))

@app.route('/errors')
def errors():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # 1. Khởi tạo thông số phân trang
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Lấy các con số tổng quát
    cursor.execute("SELECT COUNT(*) FROM Scenes")
    total_scenes = cursor.fetchone()[0] or 404
    
    cursor.execute("SELECT COUNT(*) FROM Annotations WHERE ReviewStatus = 2")
    pending_count = cursor.fetchone()[0] or 0 # Đây chính là số lỗi đang chờ

    # 3. TÍNH TOÁN CHỈ SỐ SỨC KHỎE (Sửa lỗi NameError ở đây)
    # Dùng đúng tên biến đã khai báo ở trên: pending_count và total_scenes
    health_score = round(100 - (pending_count / total_scenes * 100))

    # 4. TÍNH TOÁN PHÂN TRANG (Cần thiết cho template)
    total_pages = (pending_count + per_page - 1) // per_page
    start_idx = offset + 1
    end_idx = min(offset + per_page, pending_count)

    # 5. Lấy danh sách lỗi theo trang
    cursor.execute("""
        SELECT S.SampleToken, S.SceneName, A.ReviewDate 
        FROM Scenes S
        JOIN Annotations A ON S.SampleToken = A.SampleToken
        WHERE A.ReviewStatus = 2
        ORDER BY A.ReviewDate DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (offset, per_page))
    error_list = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM Annotations WHERE ReviewStatus = 1")
    resolved_count = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    # 6. Xác định trạng thái sức khỏe
    if health_score >= 85: health_status = "TỐT"
    elif health_score >= 60: health_status = "ỔN ĐỊNH"
    else: health_status = "RỦI RO"

    # 7. TRẢ VỀ DỮ LIỆU
    # Nếu là yêu cầu AJAX (chỉ lấy cái bảng)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('_error_table.html', 
                               error_list=error_list, page=page, 
                               total_pages=total_pages, pending_count=pending_count,
                               start_idx=start_idx, end_idx=end_idx)
    
    # Nếu load cả trang
    return render_template('errors.html',
                            health_score=health_score, 
                            health_status=health_status,
                            error_list=error_list,
                            page=page,
                            total_pages=total_pages,
                            pending_count=pending_count,
                            resolved_count=resolved_count,
                            start_idx=start_idx, 
                            end_idx=end_idx)


@app.route('/all-scenes')
def all_scenes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    # Lấy danh sách tất cả các bộ ảnh
    cursor.execute("SELECT SampleToken, imgpath_front FROM Scenes")
    rows = cursor.fetchall()
    conn.close()
    
    return render_template('all_scenes.html', scenes=rows)

@app.route('/load-more-activity')
def load_more_activity():
    offset = request.args.get('offset', 5, type=int)
    limit = 5
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query có tính toán DiffMinutes (hiệu số phút giữa hiện tại và lúc review)
    query = """
        SELECT SampleToken, ReviewStatus, 
               DATEDIFF(MINUTE, ReviewDate, GETDATE()) as DiffMinutes
        FROM Annotations
        ORDER BY ReviewDate DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """
    cursor.execute(query, (offset, limit))
    
    # Chuyển kết quả thành Dictionary để Jinja2 dễ đọc (item.SampleToken)
    columns = [column[0] for column in cursor.description]
    history = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return render_template('_activity_rows.html', history=history)

@app.route('/dataset/<path:filename>')
def serve_dataset(filename):
    dataset_path = get_dataset_path()
    if not dataset_path or not os.path.exists(dataset_path):
        return "Dataset not configured or missing", 404
        
    # dataset_path là thư mục chứa scene.json (VD: v1.0-mini/v1.0-mini)
    # Thư mục ảnh (samples/) thường nằm ở thư mục cha (VD: v1.0-mini)
    parent_path = os.path.dirname(dataset_path.rstrip('\\/'))
    if os.path.exists(os.path.join(parent_path, "samples")):
        serve_root = parent_path
    else:
        serve_root = dataset_path
        
    return send_from_directory(serve_root, filename)

@app.route('/api/pick_folder', methods=['GET'])
def pick_folder_api():
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Chưa đăng nhập!"}), 401
    try:
        script_path = os.path.join(app.root_path, 'pick_folder_script.py')
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        path = result.stdout.strip()
        if path:
            return jsonify({"status": "success", "path": path})
        return jsonify({"status": "cancelled"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Phát sinh lỗi: {str(e)}"})

@app.route('/api/import_dataset', methods=['POST'])
def import_dataset():
    if not session.get('logged_in'):
        return jsonify({"status": "error", "message": "Chưa đăng nhập!"}), 401
    
    data = request.get_json()
    new_path = data.get('path', '').strip()
    
    if not new_path or not os.path.exists(new_path):
        return jsonify({"status": "error", "message": "Đường dẫn không hợp lệ hoặc không tồn tại!"})
    
    # Kiểm tra xem có the scene.json trong path không để chắc chắn đây là dataset
    if not os.path.exists(os.path.join(new_path, "scene.json")):
        return jsonify({"status": "error", "message": "Không tìm thấy scene.json! Hãy chỉ định thư mục chứa các file json (VD: v1.0-mini/v1.0-mini)"})
        
    save_dataset_path(new_path)
    
    try:
        # Chạy file final_import.py để nạp lại dữ liệu
        # Vì dùng pyodbc, có thể gọi trực tiếp hàm nhưng an toàn nhất là chạy subprocess (để khỏi lỗi vòng lặp DB lock)
        from final_import import full_reload_data
        full_reload_data()
        return jsonify({"status": "success", "message": "Import Dataset thành công! Hệ thống đang tải lại..."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi nạp dữ liệu: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)