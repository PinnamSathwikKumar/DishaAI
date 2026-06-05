"""
User Routes
Dashboard, resume upload/analysis, chat, and DSA roadmap pages
"""

import os
import json
import uuid
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from database.db import query_db, execute_db
from utils.resume_parser import extract_text_from_file, clean_text, count_words
from utils.ats_scorer import score_resume
from utils.chatbot import get_bot_response

user_bp = Blueprint('user', __name__)


def login_required(f):
    """Decorator to protect routes that require user login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']

    # Get user info
    user = query_db('SELECT * FROM users WHERE id = %s', (user_id,), one=True)

    # Get recent resume scans
    resumes = query_db(
        'SELECT * FROM resumes WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 5',
        (user_id,)
    )

    # Stats
    resume_count = query_db('SELECT COUNT(*) as c FROM resumes WHERE user_id = %s', (user_id,), one=True)
    avg_score = query_db('SELECT AVG(ats_score) as avg FROM resumes WHERE user_id = %s', (user_id,), one=True)
    chat_count = query_db("SELECT COUNT(*) as c FROM chat_history WHERE user_id = %s AND role = 'user'", (user_id,), one=True)

    stats = {
        'resume_scans': resume_count['c'] if resume_count else 0,
        'avg_ats': round(avg_score['avg'] or 0, 1),
        'chats': chat_count['c'] if chat_count else 0,
    }

    return render_template('dashboard.html', user=user, resumes=resumes, stats=stats)


@user_bp.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    user_id = session['user_id']

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)

        file = request.files['resume']

        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Only PDF and DOCX files are allowed.', 'error')
            return redirect(request.url)

        # Save with unique name (temporarily)
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        try:
            # Extract text
            raw_text = extract_text_from_file(filepath)
            if not raw_text or raw_text.startswith('[Error'):
                flash('Could not extract text from the file. Please ensure it is not image-based.', 'error')
                os.remove(filepath)
                return redirect(request.url)

            text = clean_text(raw_text)

            # Score resume
            analysis = score_resume(text)

            # Save metadata to DB (not the file content)
            resume_id = execute_db(
                '''INSERT INTO resumes 
                   (user_id, filename, ats_score, word_count, skills_found, missing_keywords, weak_verbs_found, suggestions)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                (
                    user_id,
                    filename,
                    analysis['total_score'],
                    analysis['word_count'],
                    analysis['skills_found'],
                    analysis['missing_keywords'],
                    analysis['weak_verbs_found'],
                    json.dumps(analysis['suggestions'])
                )
            )

            # Delete file after processing (privacy + storage)
            os.remove(filepath)

            # Store analysis in session for results page
            session['last_analysis'] = {
                'resume_id': resume_id,
                'filename': filename,
                'score': analysis['total_score'],
                'grade': analysis['grade'],
                'word_count': analysis['word_count'],
                'skills': json.loads(analysis['skills_found']),
                'missing': json.loads(analysis['missing_keywords']),
                'weak_verbs': json.loads(analysis['weak_verbs_found']),
                'suggestions': analysis['suggestions'],
                'has_email': analysis.get('has_email'),
                'has_phone': analysis.get('has_phone'),
                'has_linkedin': analysis.get('has_linkedin'),
                'has_github': analysis.get('has_github'),
                'keyword_score': analysis.get('keyword_score'),
                'verb_score': analysis.get('verb_score'),
                'format_score': analysis.get('format_score'),
                'length_score': analysis.get('length_score'),
                'contact_score': analysis.get('contact_score'),
            }

            flash('Resume analyzed successfully! 🎉', 'success')
            return redirect(url_for('user.resume_result'))

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            flash(f'Error analyzing resume: {str(e)}', 'error')
            return redirect(request.url)

    # GET - show upload form with history
    history = query_db(
        'SELECT * FROM resumes WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 10',
        (user_id,)
    )
    return render_template('resume_upload.html', history=history)


@user_bp.route('/resume/result')
@login_required
def resume_result():
    analysis = session.get('last_analysis')
    if not analysis:
        flash('No analysis found. Please upload a resume.', 'info')
        return redirect(url_for('user.resume'))
    return render_template('resume_result.html', analysis=analysis)


@user_bp.route('/chat')
@login_required
def chat():
    user_id = session['user_id']
    history = query_db(
        'SELECT role, message, created_at FROM chat_history WHERE user_id = %s ORDER BY created_at ASC',
        (user_id,)
    )
    return render_template('chat.html', history=history)


@user_bp.route('/dsa-roadmap')
@login_required
def dsa_roadmap():
    # Fetch resources grouped by category
    topics = query_db(
        "SELECT * FROM dsa_resources WHERE category='topic' AND is_active ORDER BY order_index",
    )
    youtube = query_db(
        "SELECT * FROM dsa_resources WHERE category='youtube' AND is_active ORDER BY order_index",
    )
    platforms = query_db(
        "SELECT * FROM dsa_resources WHERE category='platform' AND is_active ORDER BY order_index",
    )
    suggestions = query_db(
    """
    SELECT *
    FROM suggestions
    WHERE is_active = TRUE
    ORDER BY created_at DESC
    """
)
    return render_template('dsa_roadmap.html', topics=topics, youtube=youtube, platforms=platforms, suggestions=suggestions)


@user_bp.route('/profile')
@login_required
def profile():

    user_id = session.get('user_id')

    if not user_id:
        flash('Please login first', 'error')
        return redirect(url_for('auth.login'))

    user = query_db(
        'SELECT * FROM users WHERE id = %s',
        (user_id,),
        one=True
    )

    if not user:
        session.clear()

        flash('User account not found', 'error')
        return redirect(url_for('auth.login'))

    resumes = query_db(
        '''
        SELECT *
        FROM resumes
        WHERE user_id = %s
        ORDER BY uploaded_at DESC
        ''',
        (user_id,)
    )

    return render_template(
        'profile.html',
        user=user,
        resumes=resumes
    )