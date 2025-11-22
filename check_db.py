import os
import pyodbc
from dotenv import load_dotenv

# Tải các biến từ file .env
load_dotenv()

# Lấy chuỗi kết nối từ file .env
connection_string = os.environ.get('SQLALCHEMY_DATABASE_URI')

if not connection_string:
    print("Lỗi: Không tìm thấy chuỗi kết nối SQLALCHEMY_DATABASE_URI trong file .env")
else:
    # Xóa phần tiền tố của SQLAlchemy để pyodbc có thể sử dụng
    # Ví dụ: 'mssql+pyodbc://' -> ''
    if 'mssql+pyodbc://' in connection_string:
        connection_string = connection_string.split('://', 1)[1]

    print(f"--- Đang cố gắng kết nối với chuỗi: ---\n{connection_string}\n------------------------------------")

    cnxn = None
    try:
        # Kết nối trực tiếp bằng pyodbc
        cnxn = pyodbc.connect(connection_string, autocommit=True)
        cursor = cnxn.cursor()

        print(">>> KẾT NỐI THÀNH CÔNG! <<<\n")

        # Lấy thông tin driver đang thực sự được sử dụng
        driver_name = cnxn.getinfo(pyodbc.SQL_DRIVER_NAME)
        driver_ver = cnxn.getinfo(pyodbc.SQL_DRIVER_VER)
        print(f"Driver đang sử dụng: {driver_name}")
        print(f"Phiên bản Driver: {driver_ver}\n")

        # Thử ghi đè và đọc lại dữ liệu tiếng Việt
        print("--- Đang thử UPDATE và SELECT dữ liệu tiếng Việt ---")
        test_value = 'Đã cập nhật'
        cursor.execute("UPDATE VaiTro SET TenVaiTro = ? WHERE MaVaiTro = 3", test_value)

        row = cursor.execute("SELECT TenVaiTro FROM VaiTro WHERE MaVaiTro = 3").fetchone()

        print(f"Giá trị gốc muốn ghi: '{test_value}'")
        if row:
            print(f"Giá trị đọc lại từ DB: '{row[0]}'")
            if row[0] == test_value:
                print("\n>>> TUYỆT VỜI! Dữ liệu tiếng Việt được xử lý chính xác. Vấn đề có thể nằm ở Flask/SQLAlchemy.")
            else:
                print("\n>>> LỖI! Dữ liệu đọc lại không khớp. Vấn đề nằm ở driver hoặc cấu hình DB.")
        else:
            print("Lỗi: Không tìm thấy dòng dữ liệu để kiểm tra.")

    except Exception as e:
        print(f">>> KẾT NỐI THẤT BẠI HOẶC CÓ LỖI XẢY RA <<<\nLỗi: {e}")

    finally:
        if cnxn:
            cnxn.close()
            print("\nĐã đóng kết nối.")