from flask import Flask
from app.routes import place_bp
from app.models import db
import os

app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates"
)

# Cấu hình ứng dụng
app.secret_key = 'place-secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance/venues.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo database
db.init_app(app)

# Tạo bảng nếu chưa có
with app.app_context():
    db.create_all()

# Đăng ký blueprint với prefix
app.register_blueprint(place_bp, url_prefix="/place")

if __name__ == '__main__':
    print("📂 Database file is at:", os.path.abspath("instance/venues.db"))
    app.run(port=5005, debug=True)
