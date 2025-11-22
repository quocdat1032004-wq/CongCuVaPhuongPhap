# QL/app/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class VaiTro(db.Model):
    __tablename__ = 'VaiTro'
    MaVaiTro = db.Column(db.Integer, primary_key=True)
    TenVaiTro = db.Column(db.String(50), nullable=False)
    NguoiDung = db.relationship('NguoiDung', backref='vai_tro', lazy=True)

class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'NguoiDung'
    MaNguoiDung = db.Column(db.Integer, primary_key=True)
    HoTen = db.Column(db.String(100), nullable=False)
    TenDangNhap = db.Column(db.String(50), unique=True, nullable=False)
    MatKhau = db.Column(db.String(255), nullable=False)
    MaVaiTro = db.Column(db.Integer, db.ForeignKey('VaiTro.MaVaiTro'))
    # SỬA Ở ĐÂY: Dùng 'active'/'locked'
    TrangThai = db.Column(db.String(50), default='active')
    SoDienThoai = db.Column(db.String(20), nullable=True)
    DiaChi = db.Column(db.String(255), nullable=True)

    def get_id(self):
        return str(self.MaNguoiDung)

    def set_password(self, password):
        self.MatKhau = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.MatKhau, password)

class MonAn(db.Model):
    __tablename__ = 'MonAn'
    MaMonAn = db.Column(db.Integer, primary_key=True)
    TenMonAn = db.Column(db.String(150), nullable=False)
    DonGia = db.Column(db.Numeric(18, 0), nullable=False)
    MoTa = db.Column(db.String(500))
    # SỬA Ở ĐÂY: Dùng 'selling'/'stopped'/'sold_out'
    TrangThaiBan = db.Column(db.String(50), default='selling')

class Kho(db.Model):
    __tablename__ = 'Kho'
    MaHang = db.Column(db.Integer, primary_key=True)
    TenHang = db.Column(db.String(150), nullable=False)
    SoLuongTon = db.Column(db.Integer, nullable=False, default=0)
    DonViTinh = db.Column(db.String(20))
    NguongCanhBao = db.Column(db.Integer, default=10)
    MaNguoiCapNhatCuoi = db.Column(db.Integer, db.ForeignKey('NguoiDung.MaNguoiDung'), nullable=True)
    ThoiGianCapNhatCuoi = db.Column(db.DateTime, nullable=True)

class HoaDon(db.Model):
    __tablename__ = 'HoaDon'
    MaHoaDon = db.Column(db.Integer, primary_key=True)
    NgayTao = db.Column(db.DateTime, server_default=db.func.now())
    
    # Người tạo (Khách hàng đặt online HOẶC Nhân viên bán tại quầy)
    MaNguoiDung = db.Column(db.Integer, db.ForeignKey('NguoiDung.MaNguoiDung'))
    
    # THÊM MỚI: Người xử lý (Nhân viên/Quản lý). Cho phép NULL khi mới tạo đơn online.
    MaNguoiXuLy = db.Column(db.Integer, db.ForeignKey('NguoiDung.MaNguoiDung'), nullable=True)

    TongTien = db.Column(db.Numeric(18, 0), nullable=False)
    # 'completed'/'pending'/'preparing'/'canceled'
    TrangThaiDonHang = db.Column(db.String(50), nullable=False, default='completed')
    ChiTiet = db.relationship('ChiTietHoaDon', backref='hoa_don', lazy='dynamic')
    
    # ĐỊNH NGHĨA LẠI RELATIONSHIPS:
    # Xóa dòng cũ: nguoi_dung = db.relationship('NguoiDung', backref='hoa_don', lazy=True)
    
    # Thêm các dòng mới, chỉ rõ foreign_keys:
    nguoi_tao = db.relationship('NguoiDung', foreign_keys=[MaNguoiDung], backref='hoa_don_da_tao', lazy=True)
    nguoi_xu_ly = db.relationship('NguoiDung', foreign_keys=[MaNguoiXuLy], backref='hoa_don_da_xu_ly', lazy=True)

class ChiTietHoaDon(db.Model):
    __tablename__ = 'ChiTietHoaDon'
    MaChiTietHD = db.Column(db.Integer, primary_key=True)
    MaHoaDon = db.Column(db.Integer, db.ForeignKey('HoaDon.MaHoaDon'))
    MaMonAn = db.Column(db.Integer, db.ForeignKey('MonAn.MaMonAn'))
    SoLuong = db.Column(db.Integer, nullable=False)
    DonGia = db.Column(db.Numeric(18, 0), nullable=False)
    mon_an = db.relationship('MonAn', backref='chi_tiet_hoa_don', lazy=True)

    @property
    def ThanhTien(self):
        return self.SoLuong * self.DonGia