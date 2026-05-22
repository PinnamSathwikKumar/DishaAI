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