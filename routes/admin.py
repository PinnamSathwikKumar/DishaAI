"""
Admin Routes
Admin dashboard, DSA resource management, resume stats, user overview
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db import query_db, execute_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to protect admin-only routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Stats for dashboard cards
    user_count = query_db('SELECT COUNT(*) as c FROM users', one=True)
    resume_count = query_db('SELECT COUNT(*) as c FROM resumes', one=True)
    avg_score = query_db('SELECT AVG(ats_score) as avg FROM resumes', one=True)
    resource_count = query_db('SELECT COUNT(*) as c FROM dsa_resources WHERE is_active', one=True)

    stats = {
        'users': user_count['c'],
        'resumes': resume_count['c'],
        'avg_ats': round(avg_score['avg'] or 0, 1),
        'resources': resource_count['c'],
    }

    # Recent resume uploads (metadata only, no content)
    recent_resumes = query_db(
        '''SELECT r.*, u.name as user_name, u.email as user_email
           FROM resumes r JOIN users u ON r.user_id = u.id
           ORDER BY r.uploaded_at DESC LIMIT 20'''
    )

    # Recent users
    recent_users = query_db(
        'SELECT * FROM users ORDER BY created_at DESC LIMIT 10'
    )

    # Score distribution
    score_dist = query_db(
        '''SELECT 
            SUM(CASE WHEN ats_score >= 85 THEN 1 ELSE 0 END) as excellent,
            SUM(CASE WHEN ats_score >= 70 AND ats_score < 85 THEN 1 ELSE 0 END) as good,
            SUM(CASE WHEN ats_score >= 55 AND ats_score < 70 THEN 1 ELSE 0 END) as average,
            SUM(CASE WHEN ats_score < 55 THEN 1 ELSE 0 END) as poor
           FROM resumes''',
        one=True
    )

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_resumes=recent_resumes,
        recent_users=recent_users,
        score_dist=score_dist
    )


@admin_bp.route('/resources')
@admin_required
def resources():
    all_resources = query_db('SELECT * FROM dsa_resources ORDER BY category, order_index')
    return render_template('admin/resources.html', resources=all_resources)


@admin_bp.route('/resources/add', methods=['POST'])
@admin_required
def add_resource():
    category = request.form.get('category', '').strip()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    url = request.form.get('url', '').strip()
    difficulty = request.form.get('difficulty', 'intermediate')
    order_index = request.form.get('order_index', 0)

    if not category or not title:
        flash('Category and title are required.', 'error')
        return redirect(url_for('admin.resources'))

    execute_db(
        'INSERT INTO dsa_resources (category, title, description, url, difficulty, order_index) VALUES (%s,%s,%s,%s,%s,%s)',
        (category, title, description, url, difficulty, int(order_index))
    )
    flash(f'Resource "{title}" added successfully!', 'success')
    return redirect(url_for('admin.resources'))


@admin_bp.route('/resources/edit/<int:res_id>', methods=['GET', 'POST'])
@admin_required
def edit_resource(res_id):
    resource = query_db('SELECT * FROM dsa_resources WHERE id = %s', (res_id,), one=True)
    if not resource:
        flash('Resource not found.', 'error')
        return redirect(url_for('admin.resources'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        url = request.form.get('url', '').strip()
        difficulty = request.form.get('difficulty', 'intermediate')
        is_active = TRUE if request.form.get('is_active') else 0

        execute_db(
            'UPDATE dsa_resources SET title=%s, description=%s, url=%s, difficulty=%s, is_active=%s WHERE id=%s',
            (title, description, url, difficulty, is_active, res_id)
        )
        flash('Resource updated.', 'success')
        return redirect(url_for('admin.resources'))

    return render_template('admin/edit_resource.html', resource=resource)


@admin_bp.route('/resources/delete/<int:res_id>', methods=['POST'])
@admin_required
def delete_resource(res_id):
    execute_db('DELETE FROM dsa_resources WHERE id = %s', (res_id,))
    flash('Resource deleted.', 'success')
    return redirect(url_for('admin.resources'))


@admin_bp.route('/users')
@admin_required
def users():
    all_users = query_db(
        '''SELECT u.*, COUNT(r.id) as resume_count
           FROM users u LEFT JOIN resumes r ON u.id = r.user_id
           GROUP BY u.id ORDER BY u.created_at DESC'''
    )
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):

    user = query_db(
        'SELECT * FROM users WHERE id = %s',
        (user_id,),
        one=True
    )

    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))

    execute_db(
        'DELETE FROM users WHERE id = %s',
        (user_id,)
    )

    flash(f'User "{user["name"]}" deleted successfully.', 'success')

    return redirect(url_for('admin.users'))

@admin_bp.route('/suggestions')
@admin_required
def suggestions():
    all_suggestions = query_db('SELECT * FROM suggestions ORDER BY category, created_at DESC')
    return render_template('admin/suggestions.html', suggestions=all_suggestions)


@admin_bp.route('/suggestions/add', methods=['POST'])
@admin_required
def add_suggestion():
    category = request.form.get('category', '').strip()
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not all([category, title, content]):
        flash('All fields are required.', 'error')
        return redirect(url_for('admin.suggestions'))

    execute_db(
        'INSERT INTO suggestions (category, title, content) VALUES (%s,%s,%s)',
        (category, title, content)
    )
    flash('Suggestion added.', 'success')
    return redirect(url_for('admin.suggestions'))


@admin_bp.route('/suggestions/delete/<int:sug_id>', methods=['POST'])
@admin_required
def delete_suggestion(sug_id):
    execute_db('DELETE FROM suggestions WHERE id = %s', (sug_id,))
    flash('Suggestion deleted.', 'success')
    return redirect(url_for('admin.suggestions'))
