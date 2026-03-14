from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection

app = Flask(__name__) # 2. KHỞI TẠO BIẾN APP (Dòng này phải nằm trên các dòng @app.route)

@app.route('/workspace')
def workspace():
    conn = get_db_connection()
    if not conn:
        return "Lỗi kết nối Database!"
    
    cursor = conn.cursor()
    
    # LẤY BỘ ẢNH CHƯA DUYỆT: Dùng LEFT JOIN để tìm Scene nào chưa có trong Annotations
    query = """
                SELECT TOP 1 S.* FROM Scenes S
                LEFT JOIN Annotations A ON S.SampleToken = A.SampleToken
                WHERE A.SampleToken IS NULL
            """
    cursor.execute(query)
    row = cursor.fetchone()
    
    if not row:
        return "<h1>🎉 Tuyệt vời! Bạn đã duyệt hết dữ liệu rồi.</h1>"
    
   # Map dữ liệu để đẩy ra HTML
    cams = {
        'front': row.ImgPath_Front,
        'back': row.ImgPath_Back,
        'front_left': row.ImgPath_FrontLeft,
        'front_right': row.ImgPath_FrontRight,
        'back_left': row.ImgPath_BackLeft,
        'back_right': row.ImgPath_BackRight
    }
    token = row.SampleToken
    
    cursor.close()
    conn.close()
    return render_template('workspace.html', cams=cams, token=token)

@app.route('/verify', methods=['POST'])
def verify():
    token = request.form.get('sample_token')
    status = request.form.get('status') # 1 cho Đúng, 2 cho Sai
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Lưu kết quả kiểm định
        # Trong app.py, hàm verify
        cursor.execute("""
            INSERT INTO Annotations (SampleToken, ReviewStatus, ReviewDate)
            VALUES (?, ?, GETDATE())
        """, (token, int(status)))
        conn.commit()
    except Exception as e:
        print(f"Lỗi khi lưu: {e}")
    finally:
        cursor.close()
        conn.close()
    
    # Quay lại trang workspace để tự động hiện bộ ảnh tiếp theo
    return redirect(url_for('workspace'))

@app.route('/login')
def login():
    # Flask sẽ tự tìm file login.html trong thư mục templates
    return render_template('login.html')

@app.route('/')
@app.route('/dashboard') # Cả 2 đường dẫn đều chạy chung 1 hàm bên dưới
def dashboard():
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
                           stats=stats,
                           history=history, 
                           queue=queue_count)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/errors')
def errors():
    return render_template('errors.html')

@app.route('/all-scenes')
def all_scenes():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Lấy danh sách tất cả các bộ ảnh
    cursor.execute("SELECT SampleToken, imgpath_front FROM Scenes")
    rows = cursor.fetchall()
    conn.close()
    
    return render_template('all_scenes.html', scenes=rows)
    
if __name__ == '__main__':
    app.run(debug=True)