import pyodbc

def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=localhost;'
            'DATABASE=NuLabel_DB;'
            'UID=nulabel_user;'
            'PWD=12345;'
        )
        return conn
    except Exception as e:
        print(f"Lỗi kết nối Database: {e}")
        return None

# Kiểm tra thử kết nối
if __name__ == "__main__":
    connection = get_db_connection()
    if connection:
        print("Kết nối SQL Server thành công!")
        connection.close()