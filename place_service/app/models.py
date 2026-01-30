from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # hội trường, rạp, sân khấu ngoài trời
    capacity = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200))
    description = db.Column(db.Text)
    facilities = db.Column(db.Text)  # các tiện ích đi kèm
    price_per_hour = db.Column(db.Float)
    image_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='available')  # available/booked

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'capacity': self.capacity,
            'address': self.address,
            'description': self.description,
            'facilities': self.facilities,
            'price_per_hour': self.price_per_hour,
            'image_url': self.image_url,
            'status': self.status
        }