from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint('auth', __name__)

# auth_service
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin_logged_in'] = True
            flash('Đăng nhập thành công!', 'success')
            return redirect("http://localhost:5001/customers/dashboard?admin=true")
        else:
            flash('Sai tài khoản hoặc mật khẩu!', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))
