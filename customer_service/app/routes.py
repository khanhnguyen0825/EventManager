from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Customer, db
import requests

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/dashboard')
def dashboard():
    print("Session hiện tại:", session)
    return render_template('dashboard.html')

@customer_bp.route('/')
def manage_customers():
    customers = Customer.query.all()
    return render_template('manage_customers.html', customers=customers)

@customer_bp.route('/find_by_email')
def find_by_email():
    email = request.args.get('email')
    customer = Customer.query.filter_by(email=email).first()
    if customer:
        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email
        }
    return {}, 404

@customer_bp.route('/api/<int:id>', methods=['GET'])
def get_customer_api(id):
    customer = Customer.query.get_or_404(id)
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "history": customer.history,
        "feedback": customer.feedback
    }

@customer_bp.route('/api/auto_create', methods=['POST'])
def auto_create_customer():
    data = request.get_json()
    email = data.get('email')

    # Kiểm tra nếu khách hàng đã tồn tại qua email
    customer = Customer.query.filter_by(email=email).first()
    if customer:
        return {"id": customer.id, "name": customer.name}, 200

    # Nếu chưa có → tạo mới
    new_customer = Customer(
        name=data.get('name'),
        email=email,
        phone=data.get('phone'),
        address="Chưa cập nhật",
        history="Chưa có",
        feedback="Chưa có"
    )
    db.session.add(new_customer)
    db.session.commit()

    return {"id": new_customer.id, "name": new_customer.name}, 200

@customer_bp.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        new_customer = Customer(
            name=request.form['name'],
            address=request.form['address'],
            email=request.form['email'],
            phone=request.form['phone'],
            history="Chưa có",
            feedback=request.form['feedback']
        )
        db.session.add(new_customer)
        db.session.commit()

        flash('Khách hàng đã được thêm thành công!', 'success')
        return redirect(url_for('customer.manage_customers'))
    return render_template('customer_form.html', action='Thêm')

@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)

    if request.method == 'POST':
        customer.name = request.form['name']
        customer.address = request.form['address']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.feedback = request.form['feedback']
        db.session.commit()

        flash('Thông tin khách hàng đã được cập nhật!', 'success')
        return redirect(url_for('customer.manage_customers'))

    # Gọi API bên event_service để lấy danh sách sự kiện
    events = []
    try:
        res = requests.get(f"http://localhost:5002/events/api/by_customer/{id}")
        if res.status_code == 200:
            events = res.json()
    except Exception as e:
        print("Lỗi khi lấy danh sách sự kiện:", e)

    return render_template('customer_form.html', customer=customer, events=events)


@customer_bp.route('/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)

    # Gọi sang event_service để xóa sự kiện liên quan
    try:
        requests.delete(f"http://localhost:5002/events/api/delete_by_customer/{id}")
    except Exception as e:
        print("Lỗi khi gọi event_service:", e)

    db.session.delete(customer)
    db.session.commit()

    flash('Khách hàng và các sự kiện liên quan đã được xóa!', 'success')
    return redirect(url_for('customer.manage_customers'))
