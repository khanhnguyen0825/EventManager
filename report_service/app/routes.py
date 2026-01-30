from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import db, Report
import requests

report_bp = Blueprint('report', __name__)
EVENT_SERVICE_URL = "http://localhost:5002/events/api"
CUSTOMER_SERVICE_URL = "http://localhost:5001/customers/api"

# Viết báo cáo cho sự kiện
@report_bp.route('/write/<int:event_id>', methods=['GET', 'POST'])
def write_report(event_id):
    try:
        res = requests.get(f"{EVENT_SERVICE_URL}/detail/{event_id}")
        event = res.json() if res.status_code == 200 else None
    except:
        event = None

    if not event:
        flash("Không tìm thấy sự kiện!", "danger")
        return redirect(url_for('report.completed_events'))

    try:
        customer_res = requests.get(f"{CUSTOMER_SERVICE_URL}/{event['customer_id']}")
        customer_data = customer_res.json() if customer_res.status_code == 200 else {}
        event["customer_name"] = customer_data.get("name", "Không rõ")
    except:
        event["customer_name"] = "Không rõ"

    if request.method == 'POST':
        new_report = Report(
            event_id=event_id,
            summary=request.form['summary'],
            feedback=request.form['feedback']
        )
        db.session.add(new_report)
        db.session.commit()

        try:
            requests.post(f"{EVENT_SERVICE_URL}/complete/{event_id}")
        except:
            flash("Không thể đánh dấu sự kiện hoàn thành.", "warning")

        flash("Báo cáo đã được lưu!", "success")
        return redirect("http://localhost:5002/events/")

    return render_template('write_report.html', event=event)

# Xem & cập nhật báo cáo
@report_bp.route('/view/<int:report_id>', methods=['GET', 'POST'])
def view_report(report_id):
    report = Report.query.get_or_404(report_id)

    try:
        res = requests.get(f"{EVENT_SERVICE_URL}/detail/{report.event_id}")
        event = res.json() if res.status_code == 200 else {}
    except:
        event = {}

    try:
        res = requests.get(f"{CUSTOMER_SERVICE_URL}/{event.get('customer_id')}")
        customer_data = res.json() if res.status_code == 200 else {}
        event["customer_name"] = customer_data.get("name", "Không rõ")
    except:
        event["customer_name"] = "Không rõ"

    if request.method == 'POST':
        report.summary = request.form['summary']
        report.feedback = request.form['feedback']
        db.session.commit()
        flash("Báo cáo đã được cập nhật!", "success")
        return redirect(url_for('report.report_list'))

    return render_template('view_report.html', report=report, event=event)

# Danh sách sự kiện đã hoàn thành
@report_bp.route('/completed', methods=['GET'])
def completed_events():
    try:
        res = requests.get(f"{EVENT_SERVICE_URL}/completed")
        events = res.json() if res.status_code == 200 else []
    except:
        events = []
        flash("Không thể kết nối đến event_service", "danger")

    reports = Report.query.all()
    report_map = {r.event_id: r for r in reports}

    for event in events:
        report = report_map.get(event["id"])
        event["report"] = {
            "summary": report.summary if report else "",
            "feedback": report.feedback if report else ""
        }
        event["report_id"] = report.id if report else None

        try:
            res_cust = requests.get(f"{CUSTOMER_SERVICE_URL}/{event['customer_id']}")
            customer_data = res_cust.json() if res_cust.status_code == 200 else {}
            event["customer_name"] = customer_data.get("name", "Không rõ")
        except:
            event["customer_name"] = "Không rõ"

    return render_template('completed_events.html', events=events)

# Danh sách báo cáo
@report_bp.route('/list', methods=['GET'])
def report_list():
    reports = Report.query.all()
    report_items = []

    for r in reports:
        try:
            event_res = requests.get(f"{EVENT_SERVICE_URL}/detail/{r.event_id}")
            event = event_res.json() if event_res.status_code == 200 else {}
        except:
            event = {}
        try:
            cust_res = requests.get(f"{CUSTOMER_SERVICE_URL}/{event.get('customer_id')}")
            customer_data = cust_res.json() if cust_res.status_code == 200 else {}
            customer_name = customer_data.get("name", "Không rõ")
        except:
            customer_name = "Không rõ"

        report_items.append({
            "id": r.id,
            "summary": r.summary,
            "feedback": r.feedback,
            "event_name": event.get("name", "Không rõ"),
            "event_date": event.get("date", "Không rõ"),
            "customer_name": customer_name
        })

    return render_template('report_list.html', reports=report_items)
