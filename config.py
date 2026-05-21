"""
Configuration module - MySQL setup
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- Core ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-xyz123')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'

    # --- MySQL Database ---
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '@Sathwik2005')
    DB_NAME = os.environ.get('DB_NAME', 'career_ai')

    # --- File Upload ---
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

    # --- Admin ---
    ADMIN_DEFAULT_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@careerAI.com').lower()
    ADMIN_DEFAULT_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')