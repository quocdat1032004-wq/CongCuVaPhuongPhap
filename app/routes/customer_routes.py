# QL/app/routes/customer_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
# Đảm bảo import đủ các model, bao gồm cả Kho nếu bạn dùng nó để quản lý tồn
from ..models import MonAn, HoaDon, ChiTietHoaDon, Kho 
from .. import db
from sqlalchemy import func
from functools import wraps

customer_bp = Blueprint('customer', __name__)

# --- Hàm kiểm tra quyền (Chỉ cho phép Thực khách) ---
def customer_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Kiểm tra vai trò dựa trên relationship 'vai_tro' đã được định nghĩa trong models
        if not current_user.is_authenticated or not hasattr(current_user, 'vai_tro') or current_user.vai_tro.TenVaiTro != 'Thực khách':
            flash('Chức năng này chỉ dành cho Thực khách.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Các hàm hỗ trợ quản lý kho (Tương tự order_routes.py) ---
def _inv_for_dish(mon_an):
    """Tìm record kho theo tên món (lowercase)"""
    # Giả định rằng tên món ăn khớp với tên hàng trong kho
    return Kho.query.filter(func.lower(Kho.TenHang) == func.lower(mon_an.TenMonAn)).first()

def _set_selling_state(mon_an, inv):
    """Tự động trạng thái bán dựa theo tồn kho"""
    if inv and inv.SoLuongTon <= 0:
        inv.SoLuongTon = 0
        mon_an.TrangThaiBan = 'sold_out'
    elif inv and inv.SoLuongTon > 0 and mon_an.TrangThaiBan == 'sold_out':
        mon_an.TrangThaiBan = 'selling'

# --- Routes ---

@customer_bp.route('/my_orders')
@customer_required
def my_orders():
    # Lấy lịch sử đơn hàng của người dùng hiện tại
    orders = HoaDon.query.filter_by(MaNguoiDung=current_user.MaNguoiDung)\
                         .order_by(HoaDon.NgayTao.desc()).all()
    return render_template('customer/my_orders.html', orders=orders)

@customer_bp.route('/cart')
@customer_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = {}
    total = 0
    
    if cart:
        # Lấy thông tin món ăn từ database dựa trên ID trong giỏ
        # Chuyển key từ string về int để truy vấn
        dish_ids = [int(id) for id in cart.keys() if id.isdigit()]
        dishes = MonAn.query.filter(MonAn.MaMonAn.in_(dish_ids)).all()
        
        for dish in dishes:
            # Sử dụng string làm key để lấy số lượng từ session
            quantity = cart.get(str(dish.MaMonAn))
            item_total = dish.DonGia * quantity
            total += item_total
            # Cấu trúc dữ liệu để template cart.html hiển thị
            cart_items[dish.MaMonAn] = {
                'id': dish.MaMonAn,
                'name': dish.TenMonAn,
                'price': dish.DonGia,
                'quantity': quantity
            }
            
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@customer_bp.route('/add_to_cart/<int:dish_id>', methods=['POST'])
@customer_required
def add_to_cart(dish_id):
    # Lưu ý: Để hàm này hoạt động, bạn cần thêm nút "Thêm vào giỏ hàng" trong menu/list.html
    dish = MonAn.query.get_or_404(dish_id)
    
    # Kiểm tra trạng thái bán
    if dish.TrangThaiBan != 'selling':
        flash(f'Món "{dish.TenMonAn}" hiện không khả dụng.', 'warning')
        return redirect(request.referrer or url_for('menu.list_dishes'))

    # Kiểm tra tồn kho
    inv = _inv_for_dish(dish)
    cart = session.get('cart', {})
    # Sử dụng string làm key vì session JSON ưu tiên key chuỗi
    str_dish_id = str(dish_id)
    current_qty_in_cart = cart.get(str_dish_id, 0)
    
    if inv:
        if inv.SoLuongTon <= 0:
             flash(f'Món "{dish.TenMonAn}" đã hết hàng.', 'warning')
             return redirect(request.referrer or url_for('menu.list_dishes'))
        # Kiểm tra nếu thêm 1 nữa có vượt tồn kho không
        if (current_qty_in_cart + 1) > inv.SoLuongTon:
             flash(f'Số lượng "{dish.TenMonAn}" trong giỏ đã đạt giới hạn tồn kho.', 'warning')
             return redirect(request.referrer or url_for('menu.list_dishes'))

    # Thêm vào giỏ
    cart[str_dish_id] = current_qty_in_cart + 1
    session['cart'] = cart
    
    flash(f'Đã thêm "{dish.TenMonAn}" vào giỏ hàng.', 'success')
    # Redirect về trang trước đó (thường là trang thực đơn)
    return redirect(request.referrer or url_for('menu.list_dishes'))

@customer_bp.route('/remove_from_cart/<int:dish_id>')
@customer_required
def remove_from_cart(dish_id):
    cart = session.get('cart', {})
    str_dish_id = str(dish_id)
    
    if str_dish_id in cart:
        del cart[str_dish_id]
        session['cart'] = cart
        flash('Đã xóa món ăn khỏi giỏ hàng.', 'success')
        
    return redirect(url_for('customer.view_cart'))

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@customer_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Giỏ hàng trống, không thể thanh toán.', 'warning')
        return redirect(url_for('customer.view_cart'))

    # Logic thanh toán
    try:
        # 1. Chuẩn bị dữ liệu và KIỂM TRA TỒN KHO LẦN CUỐI (Quan trọng)
        dish_ids = [int(id) for id in cart.keys() if id.isdigit()]
        dishes = MonAn.query.filter(MonAn.MaMonAn.in_(dish_ids)).all()
        
        chi_tiet = []
        tong_tien = 0
        
        for dish in dishes:
            qty = cart.get(str(dish.MaMonAn))
            inv = _inv_for_dish(dish)
            
            # Kiểm tra tồn kho trước khi tạo đơn
            if inv and qty > inv.SoLuongTon:
                flash(f'Lỗi: Số lượng "{dish.TenMonAn}" ({qty}) vượt tồn kho hiện tại ({inv.SoLuongTon}). Vui lòng cập nhật giỏ hàng.', 'danger')
                return redirect(url_for('customer.view_cart'))
            
            chi_tiet.append((dish, qty, dish.DonGia))
            tong_tien += qty * dish.DonGia

        # 2. Tạo hóa đơn
        # Trạng thái ban đầu là 'pending' (Chờ xác nhận) cho đơn online
        hd = HoaDon(MaNguoiDung=current_user.MaNguoiDung, TongTien=tong_tien, TrangThaiDonHang='pending')
        db.session.add(hd)
        db.session.flush() # Để lấy MaHoaDon mới được tạo

        # 3. Thêm chi tiết hóa đơn và TRỪ TỒN KHO
        for mon, qty, gia in chi_tiet:
            db.session.add(ChiTietHoaDon(
                MaHoaDon=hd.MaHoaDon, MaMonAn=mon.MaMonAn, SoLuong=qty, DonGia=gia
            ))
            
            # Trừ tồn và cập nhật trạng thái bán
            inv = _inv_for_dish(mon)
            if inv:
                inv.SoLuongTon -= qty
                _set_selling_state(mon, inv)

        db.session.commit()
        
        # 4. Xóa giỏ hàng sau khi đặt thành công
        session.pop('cart', None)
        
        flash('Đặt hàng thành công! Đơn hàng của bạn đang chờ xử lý.', 'success')
        return redirect(url_for('customer.my_orders'))

    except Exception as e:
        db.session.rollback()
        flash(f'Đã xảy ra lỗi khi đặt hàng: {e}', 'danger')
        return redirect(url_for('customer.view_cart'))