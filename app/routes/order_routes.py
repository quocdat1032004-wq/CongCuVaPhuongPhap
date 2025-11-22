# QL/app/routes/order_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import MonAn, HoaDon, ChiTietHoaDon
from .. import db
import datetime
from ..models import MonAn, HoaDon, ChiTietHoaDon, Kho # thêm Kho
from .. import db
import datetime
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from sqlalchemy import func

def _stock_map():
    """Map tên hàng (lower) -> tồn kho hiện tại"""
    return {k.TenHang.lower(): k for k in Kho.query.all()}

def _inv_for_dish(mon_an):
    """Tìm record kho theo tên món (lowercase)"""
    return Kho.query.filter(func.lower(Kho.TenHang) == func.lower(mon_an.TenMonAn)).first()

def _set_selling_state(mon_an, inv):
    """Tự động trạng thái bán dựa theo tồn kho"""
    if inv and inv.SoLuongTon <= 0:
        inv.SoLuongTon = 0
        # SỬA Ở ĐÂY
        mon_an.TrangThaiBan = 'sold_out'
    elif inv and inv.SoLuongTon > 0 and mon_an.TrangThaiBan == 'sold_out':
        # SỬA Ở ĐÂY
        mon_an.TrangThaiBan = 'selling'

def _today_range():
    today = datetime.date.today()
    start = datetime.datetime.combine(today, datetime.time.min)
    end   = datetime.datetime.combine(today, datetime.time.max)
    return start, end

order_bp = Blueprint('order', __name__)
# (Toàn bộ code cho file này giữ nguyên như lần trước)
# ...

@order_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    dishes = MonAn.query.filter_by(TrangThaiBan='selling').all()

    # Map tồn kho theo tên món -> số lượng (để UI cảnh báo)
    stock_map = {}
    for d in dishes:
        inv = _inv_for_dish(d)
        stock_map[d.TenMonAn.lower()] = inv.SoLuongTon if inv else None

    if request.method == 'POST':
        item_ids  = request.form.getlist('item_id[]')
        quantities = request.form.getlist('quantity[]')
        if not item_ids or not quantities or len(item_ids) != len(quantities):
            flash('Dữ liệu gửi lên không hợp lệ.', 'danger')
            return redirect(url_for('order.create_order'))

        chi_tiet, tong_tien = [], 0
        for i in range(len(item_ids)):
            try:
                ma = int(item_ids[i]); qty = int(quantities[i])
            except:
                continue
            if qty <= 0:
                continue
            mon = MonAn.query.get(ma)
            if not mon:
                continue
            inv = _inv_for_dish(mon)
            if inv and qty > inv.SoLuongTon:
                flash(f"Số lượng '{mon.TenMonAn}' vượt tồn kho ({inv.SoLuongTon}).", 'danger')
                return redirect(url_for('order.create_order'))

            chi_tiet.append((mon, qty, mon.DonGia))
            tong_tien += qty * mon.DonGia

        if not chi_tiet:
            flash('Vui lòng chọn ít nhất một món với số lượng > 0.', 'warning')
            return redirect(url_for('order.create_order'))

        try:
            hd = HoaDon(MaNguoiDung=current_user.MaNguoiDung, 
                        MaNguoiXuLy=current_user.MaNguoiDung, # Gán luôn người xử lý
                        TongTien=tong_tien, 
                        TrangThaiDonHang='completed')
            db.session.add(hd); db.session.flush()  # có MaHoaDon

            for mon, qty, gia in chi_tiet:
                db.session.add(ChiTietHoaDon(
                    MaHoaDon=hd.MaHoaDon, MaMonAn=mon.MaMonAn, SoLuong=qty, DonGia=gia
                ))

            # Trừ tồn + set trạng thái bán
            for mon, qty, _ in chi_tiet:
                inv = _inv_for_dish(mon)
                if inv:
                    inv.SoLuongTon -= qty
                    _set_selling_state(mon, inv)

            db.session.commit()
            flash('Tạo hóa đơn thành công!', 'success')
            return redirect(url_for('order.view_order', order_id=hd.MaHoaDon))
        except Exception as e:
            db.session.rollback()
            flash(f'Đã xảy ra lỗi khi tạo hóa đơn: {e}', 'danger')
            return redirect(url_for('order.create_order'))

    # GET: hóa đơn hôm nay (để quản lý ngay trong trang bán hàng)
    start, end = _today_range()
    recent_orders = (HoaDon.query
                     .filter(HoaDon.NgayTao >= start, HoaDon.NgayTao <= end)
                     .order_by(HoaDon.NgayTao.desc())
                     .limit(10).all())

    return render_template('order/create.html',
                           dishes=dishes,
                           stock_map=stock_map,
                           recent_orders=recent_orders)




@order_bp.route('/history')
@login_required
def history():
    # Lấy lịch sử hóa đơn, sắp xếp mới nhất lên đầu
    orders = HoaDon.query.order_by(HoaDon.NgayTao.desc()).all()
    return render_template('order/history.html', orders=orders)

@order_bp.route('/view/<int:order_id>')
@login_required
def view_order(order_id):
    order = HoaDon.query.get_or_404(order_id)
    return render_template('order/view.html', order=order)


# @order_bp.route('/delete/<int:order_id>', methods=['POST'])
# @login_required
# def delete_order(order_id):
#     order = HoaDon.query.get_or_404(order_id)
#     # Hoàn kho (nếu có Kho matching theo tên)
#     items = order.ChiTiet.all()  # lazy='dynamic' nên cần .all()
#     for it in items:
#         mon = MonAn.query.get(it.MaMonAn)
#         inv = Kho.query.filter(db.func.lower(Kho.TenHang) == db.func.lower(mon.TenMonAn)).first()
#         if inv:
#             inv.SoLuongTon += it.SoLuong
#             # Nếu có hàng trở lại, có thể bật bán
#             if mon.TrangThaiBan == 'Hết hàng' and inv.SoLuongTon > 0:
#                 mon.TrangThaiBan = 'Đang bán'

#     # Xoá chi tiết rồi xoá hoá đơn
#     for it in items:
#         db.session.delete(it)
#     db.session.delete(order)
#     db.session.commit()
#     flash('Đã hủy hóa đơn và hoàn kho (nếu có).', 'success')
#     return redirect(url_for('order.history'))


@order_bp.route('/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = HoaDon.query.get_or_404(order_id)
    dishes = MonAn.query.all()

    current_qty = {ct.MaMonAn: ct.SoLuong for ct in order.ChiTiet.all()}

    if request.method == 'POST':
        item_ids  = request.form.getlist('item_id[]')
        quantities = request.form.getlist('quantity[]')
        if not item_ids or not quantities or len(item_ids) != len(quantities):
            flash('Dữ liệu không hợp lệ.', 'danger')
            return redirect(url_for('order.edit_order', order_id=order_id))

        new_qty = {}
        for i in range(len(item_ids)):
            try:
                ma = int(item_ids[i]); qty = int(quantities[i])
            except:
                continue
            if qty < 0: qty = 0
            new_qty[ma] = new_qty.get(ma, 0) + qty

        # Validate delta tăng
        for ma, qty_new in new_qty.items():
            old = current_qty.get(ma, 0)
            delta = qty_new - old
            if delta > 0:
                mon = MonAn.query.get(ma)
                inv = _inv_for_dish(mon)
                if inv and delta > inv.SoLuongTon:
                    flash(f"Tăng '{mon.TenMonAn}' thêm {delta} vượt tồn ({inv.SoLuongTon}).", 'danger')
                    return redirect(url_for('order.edit_order', order_id=order_id))

        try:
            # Xóa những món về 0 (hoàn kho số cũ)
            for ct in order.ChiTiet.all():
                if new_qty.get(ct.MaMonAn, 0) == 0:
                    mon = MonAn.query.get(ct.MaMonAn)
                    inv = _inv_for_dish(mon)
                    if inv:
                        inv.SoLuongTon += ct.SoLuong
                        _set_selling_state(mon, inv)
                    db.session.delete(ct)

            # Thêm/cập nhật và điều chỉnh tồn theo delta
            for ma, qty_new in new_qty.items():
                mon = MonAn.query.get(ma)
                ct = order.ChiTiet.filter_by(MaMonAn=ma).first()
                old = current_qty.get(ma, 0)
                delta = qty_new - old

                if ct and qty_new > 0:
                    ct.SoLuong = qty_new
                elif not ct and qty_new > 0:
                    db.session.add(ChiTietHoaDon(
                        MaHoaDon=order.MaHoaDon, MaMonAn=ma, SoLuong=qty_new, DonGia=mon.DonGia
                    ))

                inv = _inv_for_dish(mon)
                if inv:
                    if delta > 0: inv.SoLuongTon -= delta
                    if delta < 0: inv.SoLuongTon += (-delta)
                    _set_selling_state(mon, inv)

            # Recompute total
            new_total = 0
            for ct in order.ChiTiet.all():
                new_total += ct.SoLuong * ct.DonGia
            order.TongTien = new_total

            db.session.commit()
            flash('Cập nhật hóa đơn thành công!', 'success')
            return redirect(url_for('order.view_order', order_id=order_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi cập nhật: {e}', 'danger')
            return redirect(url_for('order.edit_order', order_id=order_id))

    stock_map = {d.TenMonAn.lower(): (_inv_for_dish(d).SoLuongTon if _inv_for_dish(d) else None) for d in dishes}
    prefill = current_qty
    return render_template('order/edit.html', dishes=dishes, order=order, stock_map=stock_map, prefill=prefill)

# -------- Delete --------
@order_bp.route('/delete/<int:order_id>', methods=['POST'], endpoint='delete_order')
@login_required
def delete_order_post(order_id):
    order = HoaDon.query.get_or_404(order_id)
    try:
        for ct in order.ChiTiet.all():
            mon = MonAn.query.get(ct.MaMonAn)
            inv = _inv_for_dish(mon)
            if inv:
                inv.SoLuongTon += ct.SoLuong
                _set_selling_state(mon, inv)
            db.session.delete(ct)
        db.session.delete(order)
        db.session.commit()
        flash('Đã xóa hóa đơn và hoàn kho.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi xóa hóa đơn: {e}', 'danger')
    return redirect(url_for('order.create_order'))  # quay về trang bán hàng

# -------- History (chỉ liệt kê, không nút) --------
# @order_bp.route('/history')
# @login_required
# def history():
#     orders = HoaDon.query.order_by(HoaDon.NgayTao.desc()).all()
#     return render_template('order/history.html', orders=orders)

# # -------- View --------
# @order_bp.route('/view/<int:order_id>')
# @login_required
# def view_order(order_id):
#     order = HoaDon.query.get_or_404(order_id)
#     return render_template('order/view.html', order=order)

@order_bp.route('/online')
@login_required
def online_orders():
    # Chỉ Quản lý và Nhân viên mới xem được trang này
    if current_user.vai_tro.TenVaiTro not in ['Quản lý', 'Nhân viên']:
        flash('Bạn không có quyền truy cập trang này.', 'danger')
        return redirect(url_for('main.index'))
        
    orders = HoaDon.query.filter(
        HoaDon.TrangThaiDonHang != 'Hoàn thành',
        HoaDon.TrangThaiDonHang != 'Đã hủy'
    ).order_by(HoaDon.NgayTao.asc()).all()
    
    return render_template('order/online_orders.html', orders=orders)

# QL/app/routes/order_routes.py

@order_bp.route('/update-status/<int:order_id>/<string:status>')
@login_required
def update_status(order_id, status):
    if current_user.vai_tro.TenVaiTro not in ['Quản lý', 'Nhân viên']:
        flash('Bạn không có quyền thực hiện hành động này.', 'danger')
        return redirect(url_for('main.index'))

    order = HoaDon.query.get_or_404(order_id)
    
    # Đảm bảo 'pending' nằm trong danh sách hợp lệ
    valid_statuses = ['pending', 'preparing', 'completed', 'canceled']
    if status not in valid_statuses:
        flash('Trạng thái không hợp lệ.', 'warning')
        return redirect(url_for('order.online_orders'))

    order.TrangThaiDonHang = status

    # THÊM LOGIC: Ghi nhận người xử lý
    # Nếu trạng thái không phải là 'pending' (tức là bắt đầu xử lý hoặc hoàn thành)
    if status != 'pending':
        order.MaNguoiXuLy = current_user.MaNguoiDung

    db.session.commit()
    flash(f'Đã cập nhật trạng thái đơn hàng #{order.MaHoaDon} thành "{status}".', 'success')
    return redirect(url_for('order.online_orders'))