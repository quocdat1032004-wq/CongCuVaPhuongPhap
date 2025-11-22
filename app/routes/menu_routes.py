# QL/app/routes/menu_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models import MonAn
from .. import db

# Dòng này tạo ra biến menu_bp
menu_bp = Blueprint('menu', __name__)

# Route để xem danh sách món ăn (UC03)
@menu_bp.route('/')
@login_required
def list_dishes():
    dishes = MonAn.query.all()
    # Bạn sẽ cần tạo file menu/list.html sau
    return render_template('menu/list.html', dishes=dishes)

# Route để thêm món ăn mới (UC04)
@menu_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_dish():
    if request.method == 'POST':
        ten_mon = request.form.get('ten_mon')
        don_gia = request.form.get('don_gia')
        mo_ta = request.form.get('mo_ta')
        trang_thai = request.form.get('trang_thai')

        new_dish = MonAn(
            TenMonAn=ten_mon,
            DonGia=don_gia,
            MoTa=mo_ta,
            TrangThaiBan=trang_thai
        )
        db.session.add(new_dish)
        db.session.commit()
        flash('Thêm món ăn thành công!', 'success')
        return redirect(url_for('menu.list_dishes'))

    # Bạn sẽ cần tạo file menu/add_edit.html sau
    return render_template('menu/add_edit.html', action="Thêm mới")

# Route để chỉnh sửa món ăn (UC04, UC05)
@menu_bp.route('/edit/<int:dish_id>', methods=['GET', 'POST'])
@login_required
def edit_dish(dish_id):
    dish = MonAn.query.get_or_404(dish_id)
    if request.method == 'POST':
        dish.TenMonAn = request.form.get('ten_mon')
        dish.DonGia = request.form.get('don_gia') # Điều chỉnh giá
        dish.MoTa = request.form.get('mo_ta')
        dish.TrangThaiBan = request.form.get('trang_thai') # Điều chỉnh trạng thái
        
        db.session.commit()
        flash('Cập nhật món ăn thành công!', 'success')
        return redirect(url_for('menu.list_dishes'))

    # Bạn sẽ cần tạo file menu/add_edit.html sau
    return render_template('menu/add_edit.html', dish=dish, action="Chỉnh sửa")

# Route để xóa món ăn (UC04)
@menu_bp.route('/delete/<int:dish_id>', methods=['POST'])
@login_required
def delete_dish(dish_id):
    dish = MonAn.query.get_or_404(dish_id)
    db.session.delete(dish)
    db.session.commit()
    flash('Xóa món ăn thành công!', 'success')
    return redirect(url_for('menu.list_dishes'))