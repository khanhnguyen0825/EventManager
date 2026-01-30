from flask import Flask
from app.routes import event_bp
from app.models import db
import os

app = Flask(
    __name__,
    static_folder="app/static",          
    template_folder="app/templates"     
)
app.secret_key = 'event-secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance/events.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# Tạo bảng Event và Ticket nếu chưa có
with app.app_context():
    db.create_all()

app.register_blueprint(event_bp, url_prefix="/events")

if __name__ == '__main__':
    print("📂 Database file is at:", os.path.abspath("customers.db"))
    app.run(port=5002, debug=True)
