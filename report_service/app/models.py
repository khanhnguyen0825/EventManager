from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, nullable=False)  # Chỉ lưu ID, không dùng ForeignKey
    summary = db.Column(db.Text, nullable=False)  # Tóm tắt kết quả
    feedback = db.Column(db.Text)  # Đánh giá thành công/thất bại
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
