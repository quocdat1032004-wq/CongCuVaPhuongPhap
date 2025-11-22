# QL/app/routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..models import NguoiDung, VaiTro
from .. import db
from ..forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

# SỬA LẠI HÀM NÀY
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = NguoiDung.query.filter_by(TenDangNhap=form.username.data).first()
        # (Xóa các dòng print debug ở đây)
        if user and user.check_password(form.password.data):
            if user.TrangThai != 'active':
                flash('Tài khoản của bạn đã bị khóa.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.index')) 
        else:
            flash('Tên đăng nhập hoặc mật khẩu không chính xác.', 'danger')
            
    return render_template('auth/login.html', form=form)

# SỬA LẠI HÀM NÀY
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Trong hàm register()
        
        existing_user = NguoiDung.query.filter_by(TenDangNhap=form.username.data).first()
        if existing_user:
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return redirect(url_for('auth.register')) # <-- NGUYÊN NHÂN LÀ ĐÂY
        

        # --- ĐẶT CODE DEBUG VÀO ĐÚNG CHỖ NÀY ---
        print("\n--- KIỂM TRA DATABASE TỪ BÊN TRONG APP ---")
        all_roles = db.session.scalars(db.select(VaiTro)).all()
        print("Các vai trò ứng dụng đang thấy:", [role.TenVaiTro for role in all_roles])
        print("-----------------------------------------\n")
        # --------------------------------------------------

        thuc_khach_role = db.session.scalars(db.select(VaiTro).filter_by(TenVaiTro='Thực khách')).first()
        if not thuc_khach_role:
            flash('Lỗi hệ thống: Không tìm thấy vai trò "Thực khách".', 'danger')
            return redirect(url_for('auth.register'))

        new_user = NguoiDung(
            HoTen=form.ho_ten.data,
            TenDangNhap=form.username.data,
            MaVaiTro=thuc_khach_role.MaVaiTro,
            TrangThai='active'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'success')
    return redirect(url_for('auth.login'))