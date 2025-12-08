# QL/run.py

from app import create_app

# Tạo một instance của ứng dụng
app = create_app()

if __name__ == '__main__':
    # Chạy ứng dụng với chế độ debug được bật
    # Chế độ debug sẽ tự động khởi động lại server khi có thay đổi trong code
    # và cung cấp thông tin gỡ lỗi chi tiết.
    # Chỉ sử dụng trong môi trường phát triển, không dùng cho sản phẩm thực tế.
    app.run(debug=True)