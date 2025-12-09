# QL — Quản Lý Nhà Hàng (Flask)

Một ứng dụng web quản lý nhà hàng/quán ăn viết bằng Flask. Ứng dụng cung cấp các chức năng cơ bản: quản lý người dùng, menu, kho, đơn hàng và báo cáo doanh thu.

**Cây thư mục chính (rút gọn)**

- `run.py` — Entry point chạy ứng dụng
- `check_db.py` — Script kiểm tra DB (nếu có)
- `hash_passwords.py` — Script / công cụ hash mật khẩu
- `requirements.txt` — Dependencies Python
- `app/` — Thư mục ứng dụng Flask
  - `app/models.py` — Định nghĩa mô hình dữ liệu
  - `app/forms.py` — Form (WTForms)
  - `app/routes/` — Các route theo module (auth, user, menu, order,...)
  - `app/templates/` — Template Jinja2
  - `app/static/` — CSS, JS, ảnh

**Tính năng chính**

- Quản lý người dùng (đăng ký, đăng nhập, phân quyền)
- Quản lý menu (thêm, sửa, xóa món)
- Quản lý tồn kho (nhập, điều chỉnh, danh sách)
- Tạo và quản lý đơn hàng (tại quán và online)
- Báo cáo doanh thu và bestsellers

**Yêu cầu**

- Python 3.8+ (hoặc 3.9/3.10)
- `pip` để cài dependencies

**Cài đặt (macOS / zsh)**

1. Tạo và kích hoạt virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

3. (Tùy dự án) Thiết lập biến môi trường nếu cần:

```bash
export FLASK_ENV=development
# hoặc biến cấu hình riêng nếu dự án sử dụng .env
```

4. Khởi tạo hoặc kiểm tra database (nếu repository có script hỗ trợ):

```bash
python check_db.py
# Hoặc chạy migration / tạo schema theo tài liệu dự án
```

**Chạy ứng dụng**

Dùng `run.py` (file hiện có trong repository):

```bash
python run.py
```

Sau đó mở trình duyệt tại `http://127.0.0.1:5000` (mặc định)

