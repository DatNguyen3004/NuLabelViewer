from flask import Flask, render_template, request # 1. Import thư viện

app = Flask(__name__) # 2. KHỞI TẠO BIẾN APP (Dòng này phải nằm trên các dòng @app.route)

# Sau đó mới đến các hàm xử lý
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/workspace')
def workspace():
    # Chỉnh sửa: Thay tên file thật từ thư mục v1.0-mini/samples của bạn vào đây
    # Giả sử bạn đã copy ảnh vào static/dataset/
    cam_data = {
        'CAM_FRONT': 'dataset/v1.0-mini/samples/CAM_FRONT/n008-2018-08-01-15-16-36-0400__CAM_FRONT__1533151603512404.jpg', 
        'CAM_FRONT_LEFT': 'dataset/v1.0-mini/samples/CAM_FRONT_LEFT/n008-2018-08-01-15-16-36-0400__CAM_FRONT_LEFT__1533151603504799.jpg',
        'CAM_FRONT_RIGHT': 'dataset/v1.0-mini/samples/CAM_FRONT_RIGHT/n008-2018-08-01-15-16-36-0400__CAM_FRONT_RIGHT__1533151603520482.jpg',
        'CAM_BACK': 'dataset/v1.0-mini/samples/CAM_BACK/n008-2018-08-01-15-16-36-0400__CAM_BACK__1533151603537558.jpg',
        'CAM_BACK_LEFT': 'dataset/v1.0-mini/samples/CAM_BACK_LEFT/n008-2018-08-01-15-16-36-0400__CAM_BACK_LEFT__1533151603547405.jpg',
        'CAM_BACK_RIGHT': 'dataset/v1.0-mini/samples/CAM_BACK_RIGHT/n008-2018-08-01-15-16-36-0400__CAM_BACK_RIGHT__1533151603528113.jpg'
    }
    
    metadata = {
        'token': '99f8d...cc52',
        'weather': 'Trời quang',
        'speed': '45.2 MPH'
    }
    
    return render_template('workspace.html', cams=cam_data, info=metadata)

@app.route('/login')
def login():
    # Flask sẽ tự tìm file login.html trong thư mục templates
    return render_template('login.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/errors')
def errors():
    return render_template('errors.html')
    
if __name__ == '__main__':
    app.run(debug=True)