
# Import Flask utilities
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import and_
from app.models import Event, Ticket, db  # Import models từ cùng package

# Import thư viện requests để gọi HTTP API của các services khác
import requests
from datetime import datetime

# Tạo Blueprint cho Event Service - giúp tổ chức code module hóa
event_bp = Blueprint('event', __name__)

# ============================================================================
# CONFIGURATION - URLs của các services khác trong hệ thống
# ============================================================================
CUSTOMER_SERVICE_URL = "http://localhost:5001/customers/api"  # Customer Service API
PLACE_SERVICE_URL = "http://localhost:5005/place/api"  # Place Service API

# ============================================================================
# HELPER FUNCTIONS - Hàm tiện ích dùng chung
# ============================================================================

def get_customer_by_id(customer_id):
    """
    Gọi API Customer Service để lấy thông tin khách hàng theo ID
    
    """
    try:
        # Gọi API Customer Service qua HTTP
        res = requests.get(f"http://localhost:5001/customers/api/{customer_id}")
        
        # Kiểm tra response thành công
        if res.status_code == 200:
            return res.json()  # Trả về data dạng dict
    except Exception as e:
        # Log lỗi nếu không kết nối được (service down, timeout, network error)
        print("Không thể kết nối customer_service:", e)
    
    # Trả về None nếu có lỗi - cho phép hệ thống vẫn hoạt động
    return None

# ============================================================================
# API ENDPOINTS - Các endpoint API cho External Services
# ============================================================================

@event_bp.route('/api/by_customer/<int:customer_id>', methods=['GET'])
def get_events_by_customer(customer_id):
    """
    API: Lấy danh sách sự kiện của một khách hàng cụ thể

    """
    # Query database: Lấy sự kiện của customer_id và chưa hoàn thành (is_completed=False)
    # Lý do filter is_completed=False: Chỉ hiển thị events đang active, không hiển thị events đã kết thúc
    events = Event.query.filter_by(customer_id=customer_id, is_completed=False).all()
    
    # Chuyển đổi từ SQLAlchemy objects → JSON format
    # List comprehension để tạo array of dictionaries
    return jsonify([
        {
            "id": e.id,
            "name": e.name,
            "date": e.date,
            "description": e.description
        } for e in events
    ])

@event_bp.route('/api/detail/<int:event_id>')
def get_event_detail(event_id):
    """
    API: Lấy chi tiết một sự kiện
    
    """
    # Query với get_or_404: Tự động trả 404 nếu không tìm thấy
    event = Event.query.get_or_404(event_id)
    
    # Trả về JSON với đầy đủ thông tin event
    return jsonify({
        'id': event.id,
        'name': event.name,
        'date': event.date,
        'description': event.description,
        'is_completed': event.is_completed,
        'customer_id': event.customer_id  # Chỉ trả ID, không gọi relationship để tránh N+1 query
    })

@event_bp.route('/api/completed', methods=['GET'])
def get_completed_events():
    """
    API: Lấy danh sách các sự kiện đã hoàn thành
    
    """
    # Query tất cả events có is_completed = True
    events = Event.query.filter_by(is_completed=True).all()
    result = []
    
    # Loop qua từng event để tính toán số vé đã đặt
    for e in events:
        # Đếm số vé có status='booked' cho event này
        booked_count = Ticket.query.filter_by(event_id=e.id, status='booked').count()
        
        # Append vào result với đầy đủ thông tin + thống kê
        result.append({
            "id": e.id,
            "name": e.name,
            "date": e.date,
            "description": e.description,
            "customer_id": e.customer_id,
            "is_completed": e.is_completed,
            "total_tickets": e.total_tickets,  # Tổng số vé của event
            "booked_count": booked_count  # Số vé đã book thực tế
        })
    
    return jsonify(result)

# ============================================================================
# BOOKING API - Core business logic: Đặt vé
# ============================================================================

@event_bp.route('/api/book_ticket', methods=['POST'])
def book_ticket():
    """
    API: Đặt vé cho sự kiện
    
    """
    # Parse JSON data từ request body (từ Public Service)
    data = request.json
    event_id = data.get('event_id')
    quantity = int(data.get('quantity', 1))  # Default 1 vé nếu không specify
    
    # Thông tin người mua vé (guest user)
    buyer_name = data.get('buyer_name')
    buyer_email = data.get('buyer_email')
    buyer_phone = data.get('buyer_phone')

    # ========================================================================
    # VALIDATION 1: Kiểm tra giới hạn 4 vé per email per event
    # ========================================================================
    # Đếm số vé email này đã đặt cho event này (status='booked')
    existing_count = Ticket.query.filter_by(
        event_id=event_id, 
        buyer_email=buyer_email, 
        status='booked'
    ).count()
    
    # Kiểm tra: Số vé đã có + số vé đang đặt có vượt quá 4 không?
    if existing_count + quantity > 4:
        return jsonify({
            'success': False, 
            'message': 'Mỗi email chỉ được đặt tối đa 4 vé cho mỗi sự kiện. Nếu cần đặt thêm, vui lòng liên hệ hotline.'
        }), 400

    # ========================================================================
    # VALIDATION 2: Kiểm tra còn đủ vé available không
    # ========================================================================
    # Query tickets với status='available' và limit theo số lượng cần đặt
    # Lý do dùng limit(): Nếu đủ vé thì luôn lấy đúng số lượng cần, tránh query thừa
    available_tickets = Ticket.query.filter_by(
        event_id=event_id, 
        status='available'
    ).limit(quantity).all()
    
    # Kiểm tra: Số vé tìm được có đủ số lượng yêu cầu không?
    if len(available_tickets) < quantity:
        return jsonify({
            'success': False, 
            'message': 'Không đủ vé cho sự kiện này!'
        }), 400

    # ========================================================================
    # BOOKING PROCESS: Update tickets từ available → booked
    # ========================================================================
    # Lấy thông tin event để dùng khi gửi email
    event = Event.query.get(event_id)
    
    # Loop qua từng ticket đã tìm được và update status
    for ticket in available_tickets:
        ticket.status = 'booked'  # Đổi status: available → booked
        ticket.booked_at = datetime.utcnow()  # Ghi timestamp đặt vé (sử dụng datetime đã import)
        
        # Lưu thông tin người đặt vé (guest user từ public service)
        # Thực tế: Vé chỉ được đặt từ trang web public, không có login
        ticket.buyer_name = buyer_name
        ticket.buyer_email = buyer_email
        ticket.buyer_phone = buyer_phone
    
    # Commit transaction: Lưu tất cả changes vào database
    # Quan trọng: Nếu không commit thì changes chỉ ở memory, không persist
    db.session.commit()

    # ========================================================================
    # EMAIL CONFIRMATION: Gửi email xác nhận + QR code
    # ========================================================================
    from app.email_service import send_ticket_confirmation
    
    # Loop qua từng ticket đã book để gửi email riêng
    for ticket in available_tickets:
        # Chuẩn bị thông tin vé để hiển thị trong email
        ticket_info = {
            'event_name': event.name,
            'ticket_code': ticket.ticket_code,  # Mã vé duy nhất (VD: EV01-1)
            'event_date': event.date or 'N/A',
            'buyer_name': ticket.buyer_name or 'N/A'
        }
        
        # Tạo dữ liệu để encode vào QR code
        # QR code này dùng để check-in tại cổng vào event
        qr_data = f"Event: {event.name}\nTicket: {ticket.ticket_code}\nDate: {ticket.booked_at}"
        
        # Gửi email (SMTP) với ticket info và QR code
        # Email service sẽ tạo QR image và attach vào email
        if ticket.buyer_email:
            send_ticket_confirmation(ticket.buyer_email, ticket_info, qr_data)

    # ========================================================================
    # RESPONSE: Trả về kết quả thành công
    # ========================================================================
    ticket_ids = [t.id for t in available_tickets]  # List các ticket IDs đã book
    return jsonify({
        'success': True, 
        'ticket_ids': ticket_ids, 
        'quantity': quantity
    })


# ============================================================================
# ADMIN VIEWS - Trang quản lý cho admin
# ============================================================================

@event_bp.route('/', methods=['GET'])
def manage_events():
    """
    Trang quản lý sự kiện (Admin view)

    """
    # Query tất cả events chưa hoàn thành (đang active)
    events = Event.query.filter_by(is_completed=False).all()
    customer_events = []  # List để nhóm events theo customer

    # Loop qua từng event để lấy thông tin customer và tính toán vé
    for event in events:
        # Gọi Customer Service API để lấy thông tin customer
        # Sử dụng helper function đã define ở trên
        customer = get_customer_by_id(event.customer_id)
        
        if customer:  # Chỉ xử lý nếu customer service trả về data
            # Tính toán số vé
            total_tickets = event.total_tickets  # Tổng số vé ban đầu
            booked_count = Ticket.query.filter_by(
                event_id=event.id, 
                status='booked'
            ).count()  # Đếm vé đã book
            available_count = total_tickets - booked_count  # Vé còn lại
            
            # Gắn thêm attributes vào event object để dùng trong template
            # (Không lưu vào DB, chỉ tồn tại trong memory)
            event.total_tickets_display = total_tickets
            event.available_tickets_display = available_count
            
            # Nhóm events theo customer (1 customer có thể có nhiều events)
            # Kiểm tra customer đã có trong list chưa
            existing = next(
                (ce for ce in customer_events if ce['customer']['id'] == customer['id']), 
                None
            )
            
            if existing:
                # Customer đã tồn tại → append event vào list events của customer đó
                existing['events'].append(event)
            else:
                # Customer chưa có → tạo entry mới
                customer_events.append({
                    "customer": customer,
                    "events": [event]  # List chứa events của customer này
                })

    # Render template HTML với data đã chuẩn bị
    # Template sẽ loop qua customer_events để hiển thị
    return render_template('manage_events.html', customer_events=customer_events)

@event_bp.route('/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    """
    Xóa sự kiện và tất cả vé liên quan
    
    """
    # Query event, trả 404 nếu không tìm thấy
    event = Event.query.get_or_404(event_id)
    
    try:
        # Bước 1: Xóa tất cả vé liên quan đến sự kiện này
        # Phải xóa tickets trước vì có foreign key constraint
        Ticket.query.filter_by(event_id=event_id).delete()
        
        # Bước 2: Xóa sự kiện
        db.session.delete(event)
        
        # Bước 3: Commit transaction để áp dụng changes
        db.session.commit()
        
        # Flash success message (hiển thị trong template)
        flash('Sự kiện đã được xóa thành công!', 'success')
    except Exception as e:
        # Nếu có lỗi, rollback tất cả changes
        print("Lỗi khi xóa sự kiện:", e)
        db.session.rollback()
        
        # Flash error message
        flash('Có lỗi xảy ra khi xóa sự kiện!', 'danger')
    
    # Redirect về trang quản lý events
    return redirect(url_for('event.manage_events'))

# Thêm sự kiện cho khách hàng
@event_bp.route('/add/<int:customer_id>', methods=['GET', 'POST'])
def add_event(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        flash("Không tìm thấy khách hàng!", "danger")
        return redirect("/events")
    
    # Lấy danh sách địa điểm từ place_service
    venues = []
    try:
        res = requests.get(f"{PLACE_SERVICE_URL}/venues")
        if res.status_code == 200:
            venues = res.json()
    except Exception as e:
        print("Lỗi khi lấy danh sách địa điểm:", e)
        flash("Không thể lấy danh sách địa điểm!", "warning")

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_type = request.form['event_type']
        guest_count = request.form['guest_count']
        event_date = request.form['event_date']
        special_requests = request.form['special_requests']
        total_tickets = int(request.form['total_tickets'])
        venue_id = request.form.get('venue_id')

        # Lấy thông tin địa điểm từ danh sách đã có (tránh gọi API lần 2)
        venue_info = None
        if venue_id:
            venue_info = next((v for v in venues if str(v.get('id')) == venue_id), None)

        # Tạo mô tả sự kiện với thông tin địa điểm
        venue_description = ""
        if venue_info:
            venue_description = f"\nĐịa điểm tổ chức: {venue_info['name']}\n"\
                              f"Địa chỉ: {venue_info['address']}\n"\
                              f"Sức chứa: {venue_info['capacity']} người"

        event_description = f"{event_type}\n"\
                          f"Số khách mời dự kiến: {guest_count}\n"\
                          f"Ngày tổ chức: {event_date}\n"\
                          f"Yêu cầu chi tiết: {special_requests}{venue_description}"


        # ====================================================================
        # GENERATE EVENT CODE: Tạo mã sự kiện tự động
        # ====================================================================
        # Format: EV + số thứ tự (VD: EV01, EV02, ...)
        # Lấy event cuối cùng trong DB để biết ID tiếp theo
        last_event = Event.query.order_by(Event.id.desc()).first()
        next_id = (last_event.id + 1) if last_event else 1  # Nếu DB rỗng thì bắt đầu từ 1
        
        # Format event_code với padding 2 chữ số (01, 02, ...)
        event_code = f"EV{next_id:02d}"  # VD: EV01, EV02, EV10, EV99

        # ====================================================================
        # CREATE EVENT: Tạo sự kiện mới
        # ====================================================================
        new_event = Event(
            name=event_name,
            customer_id=customer_id,
            date=event_date,
            description=event_description,
            total_tickets=total_tickets,
            event_code=event_code
        )
        db.session.add(new_event)
        db.session.commit()  # Commit để có event.id cho bước tiếp theo

        # ====================================================================
        # PRE-ALLOCATION: Tạo sẵn tất cả tickets cho event
        # ====================================================================
        # Lý do: Để kiểm soát số lượng vé, tránh overselling
        # Tất cả tickets có status='available' ban đầu
        # ticket_code format: EVENTCODE-số thứ tự (VD: EV01-1, EV01-2, ...)
        
        for i in range(1, total_tickets+1):
            ticket = Ticket(
                event_id=new_event.id,  # Foreign key tới event vừa tạo
                ticket_code=f"{event_code}-{i}",  # Mã vé duy nhất
                # status mặc định là 'available' (defined trong model)
            )
            db.session.add(ticket)
        
        # Commit tất cả tickets vào database
        db.session.commit()

        flash('Sự kiện đã được thêm!', 'success')
        return redirect("/events/")

    return render_template('add_event.html', customer=customer, venues=venues)

@event_bp.route('/api/complete/<int:event_id>', methods=['POST'])
def mark_event_completed(event_id):
    """
    API: Đánh dấu sự kiện đã hoàn thành

    """
    event = Event.query.get_or_404(event_id)
    event.is_completed = True  # Update flag
    db.session.commit()
    
    # Log để tracking
    print(f"[✔] Đã đánh dấu sự kiện {event_id} là hoàn thành")
    
    return {"message": "Sự kiện đã được đánh dấu hoàn thành"}, 200

@event_bp.route('/api/delete_by_customer/<int:customer_id>', methods=['DELETE'])
def delete_events_by_customer(customer_id):
    """
    API: Xóa tất cả sự kiện của một khách hàng
    
    """
    # Xóa tất cả events có customer_id này
    Event.query.filter_by(customer_id=customer_id).delete()
    db.session.commit()
    
    return {"message": "Đã xóa sự kiện của khách hàng"}, 200

def filter_description_for_public(description):
    """
    Lọc bỏ thông tin nhạy cảm trong description trước khi public
    
    """
    if not description:
        return ""
    
    # Tách description thành từng dòng
    basic_info = []
    lines = description.split('\n')
    
    # Loop qua từng dòng
    for line in lines:
        # Kiểm tra dòng có chứa keyword nhạy cảm không
        # any() trả True nếu có ít nhất 1 keyword xuất hiện
        if not any(keyword in line.lower() for keyword in 
                   ['yêu cầu chi tiết', 'sức chứa', 'số khách mời dự kiến', 'ngày tổ chức']):
            # Dòng an toàn → giữ lại
            basic_info.append(line)
    
    # Join lại thành string với newline
    return '\n'.join(basic_info)

# ============================================================================
# PUBLIC API - Endpoints cho Public Service (không cần authentication)
# ============================================================================

@event_bp.route('/api/available', methods=['GET'])
def get_available_events():
    """
    API: Lấy danh sách sự kiện còn mở bán vé
    
    """
    # Query events đang mở (chưa completed)
    events = Event.query.filter_by(is_completed=False).all()
    result = []
    
    # Build response với thông tin public-safe
    for e in events:
        # Đếm số vé đã book để hiển thị độ hot của event
        booked_count = Ticket.query.filter_by(event_id=e.id, status='booked').count()
        
        result.append({
            "id": e.id,
            "name": e.name,
            "date": e.date,
            "description": filter_description_for_public(e.description),  # ← Filtered!
            "customer_id": e.customer_id,
            "is_completed": e.is_completed,
            "total_tickets": e.total_tickets,
            "booked_count": booked_count  # Để user biết còn bao nhiêu vé
        })
    
    return jsonify(result)

# ============================================================================
# ADMIN TICKET VIEWER - Xem tất cả vé đã đặt
# ============================================================================

@event_bp.route('/viewer', methods=['GET'])
def viewer():
    """
    Trang xem danh sách vé đã đặt (Admin)
    
    """
    # Query tất cả tickets có status='booked'
    tickets = Ticket.query.filter(Ticket.status=='booked').all()
    ticket_list = []
    
    # Loop qua từng ticket để build data hiển thị
    for t in tickets:
        # Lấy event info
        event = Event.query.get(t.event_id)
        
        # ====================================================================
        # Lấy thông tin người đặt vé từ buyer_* fields
        # ====================================================================
        # Thực tế: Tất cả vé đều được đặt từ public service (guest users)
        # Thông tin lưu trực tiếp trong ticket.buyer_name, buyer_email, buyer_phone
        ticket_list.append({
            'ticket_code': t.ticket_code,
            'event_name': event.name if event else '',
            'customer_name': t.buyer_name or '',     # Tên người mua vé
            'customer_email': t.buyer_email or '',   # Email người mua vé
            'customer_phone': t.buyer_phone or '',   # SĐT người mua vé
            'booked_at': t.booked_at.strftime('%Y-%m-%d %H:%M') if t.booked_at else ''
        })
    
    # Render template với list tickets
    return render_template('viewer.html', tickets=ticket_list)

# ============================================================================
# TICKET LOOKUP API - Tra cứu vé cho users
# ============================================================================

@event_bp.route('/api/lookup_ticket', methods=['GET'])
def lookup_ticket():
    """
    API: Tra cứu vé đã đặt theo email
    
    """
    # Lấy email từ query parameters (?email=xxx)
    email = request.args.get('email')
    
    # Validate: Nếu không có email, trả về empty array
    if not email:
        return jsonify([])
    
    # Query tickets:
    # - buyer_email khớp với email tra cứu
    # - status='booked' (chỉ lấy vé đã book, không lấy vé available)
    tickets = Ticket.query.filter(
        Ticket.buyer_email == email, 
        Ticket.status == 'booked'
    ).all()
    
    # Build response
    result = []
    for t in tickets:
        # Lấy event info để hiển thị tên event
        event = Event.query.get(t.event_id)
        
        result.append({
            'ticket_code': t.ticket_code,  # Mã vé để check-in
            'event_name': event.name if event else '',  # Tên sự kiện
            'event_date': event.date if event else '',  # Ngày sự kiện
            'booked_at': t.booked_at.strftime('%Y-%m-%d %H:%M') if t.booked_at else ''  # Thời gian đặt
        })
    
    return jsonify(result)
