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
    DB_HOST = os.getenv("MYSQLHOST")
    DB_USER = os.getenv("MYSQLUSER")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD")
    DB_NAME = os.getenv("MYSQLDATABASE")
    DB_PORT = os.getenv("MYSQLPORT")

    # --- File Upload ---
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

    TECH_KEYWORDS = [ "python", "java", "sql", "react", "flask", "django", "machine learning", "docker", "aws", "git", "github", "tensorflow" ] 
    STRONG_ACTION_VERBS = [ "developed", "engineered", "optimized", "designed", "implemented", "architected", "deployed", "built" ] 
    WEAK_ACTION_VERBS = [ "worked", "helped", "did", "made", "handled", "used" ]

    # --- AI / OpenAI ---
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    USE_AI_CHATBOT = bool(OPENAI_API_KEY)

    # --- Admin ---
    ADMIN_DEFAULT_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@careerAI.com').lower()
    ADMIN_DEFAULT_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')