from flask import Flask
from app.models import db
from app.routes import report_bp
import os

app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates"
)
app.secret_key = "report-secret"

# Đường dẫn đến file DB
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance/reports.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Khởi tạo DB
db.init_app(app)
with app.app_context():
    db.create_all()
    db.session.commit()
# Đăng ký blueprint
app.register_blueprint(report_bp, url_prefix="/reports")

if __name__ == "__main__":
    print("📂 Database file is at:", db_path)
    app.run(port=5003, debug=True)
