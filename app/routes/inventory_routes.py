# QL/app/routes/inventory_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Kho
from .. import db
from ..forms import ImportItemForm, AdjustItemForm  # Import các lớp form
import datetime
from wtforms.validators import NumberRange

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required
def list_items():
    items = Kho.query.all()
    return render_template('inventory/list.html', items=items)

@inventory_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_item():
    form = ImportItemForm()
    if form.validate_on_submit():
        item = Kho.query.filter_by(TenHang=form.ten_hang.data).first()
        if item:
            item.SoLuongTon += form.so_luong.data
            flash(f'Đã cập nhật số lượng cho mặt hàng "{item.TenHang}".', 'success')
        else:
            item = Kho(
                TenHang=form.ten_hang.data,
                SoLuongTon=form.so_luong.data,
                DonViTinh=form.don_vi_tinh.data,
                NguongCanhBao=form.nguong_canh_bao.data
            )
            db.session.add(item)
            flash(f'Đã thêm mặt hàng mới "{item.TenHang}" vào kho.', 'success')
        
        item.MaNguoiCapNhatCuoi = current_user.MaNguoiDung
        item.ThoiGianCapNhatCuoi = datetime.datetime.now()
        
        db.session.commit()
        return redirect(url_for('inventory.list_items'))

    return render_template('inventory/import_adjust.html', form=form, action="Nhập hàng")

@inventory_bp.route('/adjust/<int:item_id>', methods=['GET', 'POST'])
@login_required
def adjust_item(item_id):
    item = Kho.query.get_or_404(item_id)
    form = AdjustItemForm()
    # Validator để đảm bảo không xuất quá số lượng tồn
    form.so_luong_dieu_chinh.validators.append(NumberRange(max=item.SoLuongTon, message="Số lượng xuất không được lớn hơn tồn kho."))

    if form.validate_on_submit():
        item.SoLuongTon -= form.so_luong_dieu_chinh.data
        item.MaNguoiCapNhatCuoi = current_user.MaNguoiDung
        item.ThoiGianCapNhatCuoi = datetime.datetime.now()
        db.session.commit()
        flash('Điều chỉnh/xuất kho thành công!', 'success')
        return redirect(url_for('inventory.list_items'))
            
    return render_template('inventory/import_adjust.html', form=form, item=item, action="Điều chỉnh / Xuất kho")