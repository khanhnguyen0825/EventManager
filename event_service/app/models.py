from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_code = db.Column(db.String(10), unique=True, nullable=True)  # Mã sự kiện
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_by_customer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, nullable=False)  # Không dùng ForeignKey
    is_completed = db.Column(db.Boolean, default=False)
    total_tickets = db.Column(db.Integer, nullable=False, default=0)  # Tổng số vé cho sự kiện


# Model Ticket quản lý vé concert
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    customer_id = db.Column(db.Integer, nullable=True)  # Người đặt vé, có thể null nếu chưa đặt
    status = db.Column(db.String(20), default='available')  # available/booked/cancelled
    booked_at = db.Column(db.DateTime, nullable=True)
    ticket_code = db.Column(db.String(30), unique=True, nullable=True)  # Mã vé duy nhất
    # Thông tin khách mua vé (chỉ lưu cho buyer, không liên kết customer_service)
    buyer_name = db.Column(db.String(100))
    buyer_email = db.Column(db.String(100))
    buyer_phone = db.Column(db.String(20))

