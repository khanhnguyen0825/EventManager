from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Bạn cần đăng nhập quản trị để truy cập!", "warning")
            return redirect("http://localhost:5000/")
        return f(*args, **kwargs)
    return decorated_function
