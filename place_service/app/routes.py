from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from app.models import db, Venue
from datetime import datetime

place_bp = Blueprint('place', __name__, url_prefix='/place')

# API endpoints
@place_bp.route('/api/venues', methods=['GET'])
def get_venues():
    venues = Venue.query.all()
    return jsonify([venue.to_dict() for venue in venues])

@place_bp.route('/api/venues/<int:id>', methods=['GET'])
def get_venue(id):
    venue = Venue.query.get_or_404(id)
    return jsonify(venue.to_dict())

@place_bp.route('/api/venues', methods=['POST'])
def create_venue_api():  # Renamed to avoid conflict
    data = request.get_json()
    new_venue = Venue(
        name=data['name'],
        type=data['type'],
        capacity=data['capacity'],
        address=data['address'],
        description=data.get('description', ''),
        facilities=data.get('facilities', ''),
        price_per_hour=data['price_per_hour'],
        image_url=data.get('image_url', '')
    )
    db.session.add(new_venue)
    db.session.commit()
    return jsonify(new_venue.to_dict()), 201

@place_bp.route('/api/venues/<int:id>', methods=['PUT'])
def update_venue_api(id):  # Renamed to avoid conflict
    venue = Venue.query.get_or_404(id)
    data = request.get_json()
    
    venue.name = data.get('name', venue.name)
    venue.type = data.get('type', venue.type)
    venue.capacity = data.get('capacity', venue.capacity)
    venue.address = data.get('address', venue.address)
    venue.description = data.get('description', venue.description)
    venue.facilities = data.get('facilities', venue.facilities)
    venue.price_per_hour = data.get('price_per_hour', venue.price_per_hour)
    venue.image_url = data.get('image_url', venue.image_url)
    venue.status = data.get('status', venue.status)
    
    db.session.commit()
    return jsonify(venue.to_dict())

@place_bp.route('/api/venues/<int:id>', methods=['DELETE'])
def delete_venue_api(id):  # Renamed to avoid conflict
    venue = Venue.query.get_or_404(id)
    db.session.delete(venue)
    db.session.commit()
    return '', 204

# Web routes
@place_bp.route('/')
def index():
    venues = Venue.query.all()
    return render_template('manage_place.html', venues=venues)

@place_bp.route('/venues/new', methods=['GET', 'POST'])
def new_venue():
    if request.method == 'POST':
        new_venue = Venue(
            name=request.form['name'],
            type=request.form['type'],
            capacity=int(request.form['capacity']),
            address=request.form['address'],
            description=request.form.get('description', ''),
            facilities=request.form.get('facilities', ''),
            price_per_hour=float(request.form['price_per_hour']),
            image_url=request.form.get('image_url', '')
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('Địa điểm đã được thêm thành công!', 'success')
        return redirect(url_for('place.index'))
    return render_template('add_place.html')

@place_bp.route('/venues/<int:id>/edit', methods=['GET', 'POST'])
def edit_venue(id):
    venue = Venue.query.get_or_404(id)
    if request.method == 'POST':
        venue.name = request.form['name']
        venue.type = request.form['type']
        venue.capacity = int(request.form['capacity'])
        venue.address = request.form['address']
        venue.description = request.form.get('description', '')
        venue.facilities = request.form.get('facilities', '')
        venue.price_per_hour = float(request.form['price_per_hour'])
        venue.image_url = request.form.get('image_url', '')
        
        db.session.commit()
        flash('Địa điểm đã được cập nhật thành công!', 'success')
        return redirect(url_for('place.index'))
    return render_template('edit_place.html', venue=venue)

@place_bp.route('/venues/<int:id>/delete', methods=['POST'])
def delete_venue_web(id):
    venue = Venue.query.get_or_404(id)
    db.session.delete(venue)
    db.session.commit()
    flash('Địa điểm đã được xóa thành công!', 'success')
    return redirect(url_for('place.index'))