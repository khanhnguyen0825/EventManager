from flask import Blueprint, render_template, request, url_for, redirect, flash
import requests

public_bp = Blueprint('public', __name__)
CUSTOMER_SERVICE_URL = "http://localhost:5001/customers"
EVENT_SERVICE_URL = "http://localhost:5002/events/api"


# Route: Đặt vé concert (landing page mới)
@public_bp.route('/register', methods=['GET', 'POST'])
def book_ticket_public():
    events = []
    if request.method == 'GET':
        # Lấy danh sách sự kiện từ event_service
        try:
            res = requests.get(f"{EVENT_SERVICE_URL}/available")
            if res.status_code == 200:
                events = res.json()
        except Exception as e:
            print("Lỗi lấy danh sách sự kiện:", e)
        return render_template("register_event.html", events=events)

    # POST: Khách đặt vé
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    event_id = request.form['event_id']
    ticket_quantity = int(request.form.get('ticket_quantity', 1))

    # Nếu là khách mua vé concert, không tạo customer, chỉ gửi thông tin sang event_service
    try:
        res = requests.post(f"{EVENT_SERVICE_URL}/book_ticket", json={
            "event_id": event_id,
            "quantity": ticket_quantity,
            "buyer_name": name,
            "buyer_email": email,
            "buyer_phone": phone
        })
        data = res.json()
        if data.get('success'):
            flash(f"Đặt vé thành công! Đã đặt {ticket_quantity} vé.", "success")
        else:
            flash(data.get('message', 'Đặt vé thất bại!'), "danger")
    except Exception as e:
        print("Lỗi đặt vé:", e)
        flash("Lỗi khi đặt vé!", "danger")
    return redirect(url_for('public.book_ticket_public'))

# Route: Tra cứu sự kiện
@public_bp.route('/lookup', methods=['GET', 'POST'])
def check_events():
    tickets = []
    email_checked = None

    if request.method == 'POST':
        email_checked = request.form.get('lookup_email')
        # Gọi event_service để tra cứu vé theo email
        try:
            res = requests.get(f"{EVENT_SERVICE_URL}/lookup_ticket", params={"email": email_checked})
            if res.status_code == 200:
                tickets = res.json()
        except Exception as e:
            print("Lỗi tra cứu vé:", e)

    return render_template('check_results.html', tickets=tickets, email_checked=email_checked)
