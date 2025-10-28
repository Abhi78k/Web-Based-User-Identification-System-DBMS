from flask import Blueprint, render_template, redirect, url_for, flash, request, session as flask_session
from flask_login import login_required
from functools import wraps
import pymysql
from config import Config
from utils.logging import get_audit_logs, create_audit_log
from utils.sessions import get_all_sessions

admin_bp = Blueprint('admin', __name__)

def get_db_connection():
    """Create and return a database connection."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if flask_session.get('role') != 'Admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return wrapper

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard page."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Get user statistics
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM Users")
            total_users = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM Roles")
            total_roles = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM Sessions")
            total_sessions = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM AuditLogs")
            total_logs = cursor.fetchone()['count']
        
        conn.close()
        
        stats = {
            'total_users': total_users,
            'total_roles': total_roles,
            'total_sessions': total_sessions,
            'total_logs': total_logs
        }
        
        return render_template('admin_dashboard.html', stats=stats)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        conn.close()
        return redirect(url_for('auth.login'))

@admin_bp.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def admin_users():
    """View and manage users."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.role_name 
                FROM Users u 
                LEFT JOIN Roles r ON u.role_id = r.role_id 
                ORDER BY u.created_at DESC
            """)
            users = cursor.fetchall()
        
        # Get all roles
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Roles")
            roles = cursor.fetchall()
        
        conn.close()
        return render_template('admin_users.html', users=users, roles=roles)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        conn.close()
        return redirect(url_for('dashboard.dashboard'))

@admin_bp.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    """Change user role."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin.admin_users'))
    
    try:
        new_role_id = request.form.get('role_id')
        
        # Get current user from session
        from flask_login import current_user
        admin_user_id = current_user.user_id
        
        with conn.cursor() as cursor:
            # Get role name for audit log
            cursor.execute("SELECT role_name FROM Roles WHERE role_id = %s", (new_role_id,))
            role = cursor.fetchone()
            role_name = role['role_name'] if role else 'Unknown'
            
            # Update user role
            cursor.execute(
                "UPDATE Users SET role_id = %s WHERE user_id = %s",
                (new_role_id, user_id)
            )
            conn.commit()
        
        create_audit_log(admin_user_id, f'Changed role for user_id {user_id} to {role_name}')
        
        conn.close()
        flash('User role updated successfully!', 'success')
        return redirect(url_for('admin.admin_users'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        conn.close()
        return redirect(url_for('admin.admin_users'))

@admin_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin.admin_users'))
    
    try:
        # Get current user from session
        from flask_login import current_user
        admin_user_id = current_user.user_id
        
        # Prevent admin from deleting themselves
        if user_id == admin_user_id:
            flash('You cannot delete your own account.', 'warning')
            conn.close()
            return redirect(url_for('admin.admin_users'))
        
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
            conn.commit()
        
        create_audit_log(admin_user_id, f'Deleted user_id {user_id}')
        
        conn.close()
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin.admin_users'))
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        conn.close()
        return redirect(url_for('admin.admin_users'))

@admin_bp.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    """View system logs."""
    try:
        audit_logs = get_audit_logs(limit=100)
        sessions = get_all_sessions(limit=100)
        
        return render_template('admin_logs.html', audit_logs=audit_logs, sessions=sessions)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

