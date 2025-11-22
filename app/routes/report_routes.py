# QL/app/routes/report_routes.py
from flask import Blueprint, render_template, request
from flask_login import login_required
from ..models import HoaDon, ChiTietHoaDon, MonAn
from .. import db
from sqlalchemy import func
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
import io, csv
from flask import send_file


report_bp = Blueprint('report', __name__)
# Route cho báo cáo doanh thu (UC10)
@report_bp.route('/revenue')
@login_required
def revenue_report():
    period = request.args.get('period', 'today')
    today = datetime.now().date()
    
    if period == 'today':
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        title = "Hôm nay"
    elif period == 'weekly':
        start_date = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        end_date = datetime.combine(start_date.date() + timedelta(days=6), datetime.max.time())
        title = "Tuần này"
    elif period == 'monthly':
        start_date = datetime.combine(today.replace(day=1), datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        title = "Tháng này"
    else: # Mặc định là hôm nay
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        title = "Hôm nay"

    # Truy vấn doanh thu
    revenue_data = db.session.query(
        func.sum(HoaDon.TongTien)
    ).filter(
        HoaDon.NgayTao >= start_date,
        HoaDon.NgayTao <= end_date
    ).scalar() or 0

    orders_in_period = HoaDon.query.filter(
        HoaDon.NgayTao >= start_date,
        HoaDon.NgayTao <= end_date
    ).all()

    return render_template('report/revenue.html', 
                           total_revenue=revenue_data, 
                           orders=orders_in_period,
                           title=title,
                           current_period=period)

# Route cho thống kê món bán chạy (UC11)
@report_bp.route('/bestsellers')
@login_required
def bestsellers_report():
    # Thống kê món ăn bán chạy nhất theo số lượng
    bestsellers = db.session.query(
        MonAn.TenMonAn,
        func.sum(ChiTietHoaDon.SoLuong).label('total_quantity')
    ).join(MonAn, MonAn.MaMonAn == ChiTietHoaDon.MaMonAn)\
    .group_by(MonAn.TenMonAn)\
    .order_by(func.sum(ChiTietHoaDon.SoLuong).desc())\
    .limit(10).all()

    return render_template('report/bestsellers.html', bestsellers=bestsellers)

# UC12 - Xuất báo cáo sẽ cần các thư viện ngoài như Pandas hoặc tạo file CSV.
# Đây là một ví dụ đơn giản, các chức năng phức tạp hơn sẽ được phát triển sau.
@report_bp.route('/export')
@login_required
def export_report():
    fmt = request.args.get('format', 'csv')
    period = request.args.get('period', 'today')

    # Tính khoảng thời gian giống revenue_report
    today = datetime.now().date()
    if period == 'today':
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        title = "Hôm nay"
    elif period == 'weekly':
        start_date = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        end_date = datetime.combine(start_date.date() + timedelta(days=6), datetime.max.time())
        title = "Tuần này"
    elif period == 'monthly':
        start_date = datetime.combine(today.replace(day=1), datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        title = "Tháng này"
    else:
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        title = "Hôm nay"

    orders = HoaDon.query.filter(
        HoaDon.NgayTao >= start_date,
        HoaDon.NgayTao <= end_date
    ).order_by(HoaDon.NgayTao.asc()).all()
    total_revenue = db.session.query(func.sum(HoaDon.TongTien)).filter(
        HoaDon.NgayTao >= start_date,
        HoaDon.NgayTao <= end_date
    ).scalar() or 0

    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Kỳ', title])
        writer.writerow(['Tổng doanh thu', f'{total_revenue}'])
        writer.writerow([])
        writer.writerow(['Mã HĐ', 'Ngày tạo', 'Tổng tiền'])
        for o in orders:
            writer.writerow([o.MaHoaDon, o.NgayTao.strftime('%d-%m-%Y %H:%M:%S'), int(o.TongTien)])
        data = output.getvalue().encode('utf-8-sig')
        return send_file(
            io.BytesIO(data),
            as_attachment=True,
            download_name=f'revenue_{period}.csv',
            mimetype='text/csv'
        )
    elif fmt == 'pdf':
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
        except ImportError:
            flash('Chưa cài reportlab. Vui lòng: pip install reportlab', 'danger')
            return redirect(url_for('report.revenue_report', period=period))

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 20*mm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(20*mm, y, f"Báo cáo doanh thu - {title}")
        y -= 10*mm
        c.setFont("Helvetica", 12)
        c.drawString(20*mm, y, f"Tổng doanh thu: {int(total_revenue):,} VND".replace(',', '.'))
        y -= 10*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20*mm, y, "Danh sách hóa đơn")
        y -= 8*mm
        c.setFont("Helvetica", 10)
        for o in orders:
            line = f"- #{o.MaHoaDon} | {o.NgayTao.strftime('%d-%m-%Y %H:%M')} | {int(o.TongTien):,} VND".replace(',', '.')
            c.drawString(20*mm, y, line)
            y -= 6*mm
            if y < 20*mm:
                c.showPage()
                y = height - 20*mm
                c.setFont("Helvetica", 10)

        c.showPage()
        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f'revenue_{period}.pdf', mimetype='application/pdf')
    else:
        flash('Định dạng export không hợp lệ. Dùng ?format=csv hoặc ?format=pdf', 'warning')
        return redirect(url_for('report.revenue_report', period=period))
