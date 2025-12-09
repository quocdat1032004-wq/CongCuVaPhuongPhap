# QL/hash_passwords.py

from app import create_app, db
from app.models import NguoiDung

# Tạo một instance của ứng dụng để có context
app = create_app()

with app.app_context():
    print("Bắt đầu cập nhật mật khẩu...")

    # Tìm người dùng
    nhanvien = NguoiDung.query.filter_by(TenDangNhap='nhanvien1').first()
    quanly = NguoiDung.query.filter_by(TenDangNhap='quanly1').first()
    thuckhach =NguoiDung.query.filter_by(TenDangNhap='thuckhach1').first()

    if nhanvien:
        # Đặt lại mật khẩu đã được băm
        nhanvien.set_password('matkhaunv1') 
        print("Đã cập nhật mật khẩu cho 'nhanvien1'.")
    else:
        print("Không tìm thấy người dùng 'nhanvien1'.")

    if quanly:
        # Đặt lại mật khẩu đã được băm
        quanly.set_password('matkhauql1')
        print("Đã cập nhật mật khẩu cho 'quanly1'.")
    else:
        print("Không tìm thấy người dùng 'quanly1'.")
    
    if thuckhach:
        # Đặt lại mật khẩu đã được băm
        thuckhach.set_password('matkhautk1')
        print("Đã cập nhật mật khẩu cho 'thuckhach1'.")

    # Lưu thay đổi vào database
    db.session.commit()
    print("Hoàn tất! Mật khẩu đã được mã hóa.")