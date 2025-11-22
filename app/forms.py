# QL/app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo # Đảm bảo có EqualTo

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', 
                           validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Mật khẩu', 
                             validators=[DataRequired()])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

# --- THÊM CÁC FORM CHO KHO HÀNG ---

class ImportItemForm(FlaskForm):
    ten_hang = StringField('Tên hàng hóa', validators=[DataRequired(), Length(max=150)])
    so_luong = IntegerField('Số lượng nhập', validators=[DataRequired(), NumberRange(min=1)])
    don_vi_tinh = StringField('Đơn vị tính', validators=[Length(max=20)])
    nguong_canh_bao = IntegerField('Ngưỡng cảnh báo', default=10, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Nhập hàng')

class AdjustItemForm(FlaskForm):
    loai = SelectField(
        'Loại điều chỉnh',
        choices=[('giam', 'Xuất/Giảm'), ('tang', 'Nhập bổ sung/Tăng')],
        validators=[DataRequired()]
    )
    so_luong_dieu_chinh = IntegerField(
        'Số lượng điều chỉnh/xuất',
        validators=[DataRequired(), NumberRange(min=1)]
    )
    ly_do = TextAreaField('Lý do', validators=[Length(max=255)])
    submit = SubmitField('Lưu thay đổi')

# --- THÊM FORM ĐĂNG KÝ MỚI VÀO ĐÂY ---
class RegisterForm(FlaskForm):
    ho_ten = StringField('Họ tên', validators=[DataRequired(), Length(max=100)])
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password', message='Mật khẩu không khớp.')])
    submit = SubmitField('Đăng ký')