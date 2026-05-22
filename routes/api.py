"""
API Routes
JSON endpoints for AJAX interactions (chat, etc.)
"""

from functools import wraps
from flask import Blueprint, request, jsonify, session
from database.db import execute_db, query_db
from utils.chatbot import get_bot_response

api_bp = Blueprint('api', __name__, url_prefix='/api')


def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@api_bp.route('/chat', methods=['POST'])
@api_login_required
def chat():
    """Handle chat messages. Returns AI/keyword-based response."""
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message'].strip()[:500]  # Limit message length
    user_id = session['user_id']

    # Load recent chat history for context
    history = query_db(
        'SELECT role, message FROM chat_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 10',
        (user_id,)
    )
    history = list(reversed(history))  # Chronological order

    # Get bot response
    bot_response = get_bot_response(user_message, [dict(h) for h in history])

    # Save both messages to history
    execute_db(
        'INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)',
        (user_id, 'user', user_message)
    )
    execute_db(
        'INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)',
        (user_id, 'assistant', bot_response)
    )

    return jsonify({
        'response': bot_response,
        'status': 'ok'
    })


@api_bp.route('/chat/clear', methods=['POST'])
@api_login_required
def clear_chat():
    """Clear user's chat history."""
    user_id = session['user_id']
    execute_db('DELETE FROM chat_history WHERE user_id = %s', (user_id,))
    return jsonify({'status': 'cleared'})


@api_bp.route('/stats', methods=['GET'])
@api_login_required
def stats():
    """Return user stats as JSON."""
    user_id = session['user_id']
    resumes = query_db(
        'SELECT ats_score, uploaded_at FROM resumes WHERE user_id = %s ORDER BY uploaded_at ASC',
        (user_id,)
    )
    return jsonify({
        'scores': [{'score': r['ats_score'], 'date': r['uploaded_at']} for r in resumes]
    })
