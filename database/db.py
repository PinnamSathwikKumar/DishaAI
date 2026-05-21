"""
Database module - MySQL setup
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from flask import current_app, g


def get_db():
    """Get MySQL connection stored on Flask g object."""
    print("DB HOST:", current_app.config['DB_HOST'])
    print("DB USER:", current_app.config['DB_USER'])
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME'],
                autocommit=False
            )
        except mysql.connector.Error as err:
            print("MySQL Connection Error:", err)
            raise

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if not exist."""
    conn = get_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            college VARCHAR(255),
            year VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ADMINS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # RESUMES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            ats_score INT,
            word_count INT,
            skills_found TEXT,
            missing_keywords TEXT,
            weak_verbs_found TEXT,
            suggestions TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # DSA RESOURCES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dsa_resources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            url TEXT,
            difficulty VARCHAR(50),
            order_index INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # SUGGESTIONS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # CHAT HISTORY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)


    conn.commit()
    cursor.close()
    seed_admin()
    seed_dsa_resources()

def query_db(query, args=None, one=False):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, args or ())
    result = cursor.fetchall()
    cursor.close()
    return (result[0] if result else None) if one else result


def execute_db(query, args=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, args or ())
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    return last_id

def seed_admin():
    from config import Config

    admin_email = Config.ADMIN_DEFAULT_EMAIL.lower()
    admin_password = Config.ADMIN_DEFAULT_PASSWORD

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM admins WHERE email = %s", (admin_email,))
    existing = cursor.fetchone()

    if not existing:
        cursor.execute(
            "INSERT INTO admins (email, password_hash) VALUES (%s, %s)",
            (admin_email, generate_password_hash(admin_password))
        )
        conn.commit()

    cursor.close()

def seed_dsa_resources():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM dsa_resources")
    count = cursor.fetchone()[0]

    if count == 0:
        resources = [
            ('platform', 'LeetCode', 'Industry standard coding practice', 'https://leetcode.com', 'intermediate', 1),
            ('platform', 'GeeksForGeeks', 'Theory + practice problems', 'https://geeksforgeeks.org', 'beginner', 2)
        ]

        cursor.executemany(
            """
            INSERT INTO dsa_resources
            (category, title, description, url, difficulty, order_index)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            resources
        )
        conn.commit()

    cursor.close()