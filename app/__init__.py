# QL/app/__init__.py

import os
from flask import Flask, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
# XÓA DÒNG NÀY Ở ĐẦU FILE:
# from .routes.customer_routes import customer_bp

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Đọc cấu hình từ biến môi trường đã được load_dotenv() tải lên
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'

    # Import models sau khi db đã được init
    from .models import NguoiDung
    @login_manager.user_loader
    def load_user(user_id):
        return NguoiDung.query.get(int(user_id))

    with app.app_context():
        # Import và đăng ký Blueprints (Tất cả phải nằm trong này để tránh Circular Import)
        from .routes.auth_routes import auth_bp
        from .routes.user_routes import user_bp
        from .routes.menu_routes import menu_bp
        from .routes.order_routes import order_bp
        from .routes.inventory_routes import inventory_bp
        from .routes.report_routes import report_bp
        # THÊM DÒNG IMPORT VÀO ĐÂY:
        from .routes.customer_routes import customer_bp
        
        main_bp = Blueprint('main', __name__)
        @main_bp.route('/')
        def index():
            return render_template('index.html')

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(user_bp, url_prefix='/users')
        app.register_blueprint(menu_bp, url_prefix='/menu')
        app.register_blueprint(order_bp, url_prefix='/orders')
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        app.register_blueprint(report_bp, url_prefix='/reports')
        # Đăng ký customer_bp
        app.register_blueprint(customer_bp, url_prefix='/customer')
        
        return app