"""
Authentication Routes
Handles user registration, login, logout, and admin login
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        college = request.form.get('college', '').strip()
        year = request.form.get('year', '')

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email or '@' not in email:
            errors.append('Enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        # Check if email already exists
        existing = query_db('SELECT id FROM users WHERE email = %s', (email,), one=True)
        if existing:
            errors.append('An account with this email already exists.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('register.html', form_data=request.form)

        # Create user
        password_hash = generate_password_hash(password)
        user_id = execute_db(
            'INSERT INTO users (name, email, password_hash, college, year) VALUES (%s, %s, %s, %s, %s)',
            (name, email, password_hash, college, year)
        )
        session['user_id'] = user_id
        session['user_name'] = name
        flash('Welcome to CareerAI! 🎉', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('register.html', form_data={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db('SELECT * FROM users WHERE email = %s', (email,), one=True)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome back, {user["name"]}! 👋', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))


# ─── Admin Auth ───────────────────────────────────────────────────────────────

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        admin = query_db('SELECT * FROM admins WHERE email = %s', (email,), one=True)

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_email'] = admin['email']
            flash('Admin access granted.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')

    return render_template('admin/login.html')


@auth_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    flash('Admin session ended.', 'info')
    return redirect(url_for('auth.admin_login'))
