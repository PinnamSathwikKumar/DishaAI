"""
Career AI - Main Flask Application
AI-powered career assistant platform for CSE students
"""

import os
from datetime import datetime
from flask import Flask
from config import Config
from database.db import init_db, close_db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.api import api_bp
from flask import session, redirect, url_for, flash
from database.db import query_db
from datetime import timedelta

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database
    with app.app_context():
        init_db()

    # Close DB after each request
    app.teardown_appcontext(close_db)

    app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
    )
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    # ---------------------------------------- 
    # Jinja Date Formatting Filter 
    # ----------------------------------------
    @app.template_filter('datefmt')
    def datefmt(value, fmt='%Y-%m-%d'):
        if value is None:
            return "N/A"
        if isinstance(value, datetime):
             return value.strftime(fmt)
        return value

    @app.before_request
    def validate_user_exists():

        user_id = session.get('user_id')

        if not user_id:
            return

        user = query_db(
            "SELECT id FROM users WHERE id = %s",
            (user_id,),
            one=True
        )

        if not user:
            session.clear()
            flash(
                "Your account no longer exists. Please login again.",
                "error"
            )
            return redirect(url_for('auth.login'))

        admin_id = session.get('admin_id')

        if admin_id:
            admin = query_db(
                "SELECT id FROM admins WHERE id = %s",
                (admin_id,),
                one=True
            )

            if not admin:
                session.clear()
                return redirect(url_for('auth.admin_login'))
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'False') == 'True',
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )