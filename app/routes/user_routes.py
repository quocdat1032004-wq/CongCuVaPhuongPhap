# QL/app/routes/user_routes.py

# QL/app/routes/user_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from functools import wraps
# SỬA LẠI DÒNG DƯỚI ĐÂY
from ..models import NguoiDung, VaiTro
from .. import db
user_bp = Blueprint('user', __name__)

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.vai_tro.TenVaiTro != 'Quản lý':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/')
@login_required
@manager_required
def list_users():
    users = NguoiDung.query.all()
    return render_template('user/list.html', users=users)

# Trong file QL/app/routes/user_routes.py

@user_bp.route('/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_user():
    roles = VaiTro.query.all()
    if request.method == 'POST':
        # CÁC DÒNG BỊ THIẾU NẰM Ở ĐÂY
        ho_ten = request.form.get('ho_ten')
        ten_dang_nhap = request.form.get('ten_dang_nhap')
        mat_khau = request.form.get('mat_khau')
        ma_vai_tro = request.form.get('ma_vai_tro')
        trang_thai = request.form.get('trang_thai')

        existing_user = NguoiDung.query.filter_by(TenDangNhap=ten_dang_nhap).first()
        if existing_user:
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return render_template('user/add_edit.html', roles=roles, action="Thêm mới")

        new_user = NguoiDung(
            HoTen=ho_ten, 
            TenDangNhap=ten_dang_nhap,
            MaVaiTro=ma_vai_tro,
            TrangThai=trang_thai
        )
        new_user.set_password(mat_khau)
        db.session.add(new_user)
        db.session.commit()
        flash('Thêm người dùng thành công!', 'success')
        return redirect(url_for('user.list_users'))
        
    return render_template('user/add_edit.html', roles=roles, action="Thêm mới")

@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_user(user_id):
    user = NguoiDung.query.get_or_404(user_id)
    roles = VaiTro.query.all()
    
    if request.method == 'POST':
        try:
            # Cập nhật thông tin cơ bản
            user.HoTen = request.form.get('ho_ten')
            user.MaVaiTro = request.form.get('ma_vai_tro')
            user.TrangThai = request.form.get('trang_thai')

            # Xử lý mật khẩu mới (chỉ cập nhật nếu người dùng nhập vào)
            mat_khau_moi = request.form.get('mat_khau')
            if mat_khau_moi:
                user.set_password(mat_khau_moi)

            db.session.commit() # <<< Lưu thay đổi vào DB
            flash('Cập nhật thông tin người dùng thành công!', 'success')
            return redirect(url_for('user.list_users'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật người dùng: {e}', 'danger')

    # Phương thức GET
    return render_template('user/add_edit.html', user=user, roles=roles, action="Chỉnh sửa")

@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@manager_required
def delete_user(user_id):
    user = NguoiDung.query.get_or_404(user_id)

    if current_user.MaNguoiDung == user.MaNguoiDung:
        flash('Bạn không thể xóa chính tài khoản của mình.', 'warning')
        return redirect(url_for('user.list_users'))
    try:
        # SỬA Ở ĐÂY
        user.TrangThai = 'locked'
        db.session.commit()
        flash('Đã khóa tài khoản người dùng.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi khóa người dùng: {e}', 'danger')
    return redirect(url_for('user.list_users'))