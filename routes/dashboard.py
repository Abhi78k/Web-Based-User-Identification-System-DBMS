from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
import pymysql
from config import Config
from utils.sessions import get_user_sessions
from utils.logging import get_audit_logs

dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page."""
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('auth.login'))
    
    try:
        # Get user information
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.role_name 
                FROM Users u 
                LEFT JOIN Roles r ON u.role_id = r.role_id 
                WHERE u.user_id = %s
            """, (current_user.user_id,))
            user_data = cursor.fetchone()
        
        conn.close()
        
        # Get user sessions
        sessions = get_user_sessions(current_user.user_id, limit=10)
        
        # Get user's audit logs
        audit_logs = []
        if user_data and user_data.get('role_name') == 'Admin':
            # Admins can see all logs
            audit_logs = get_audit_logs(limit=20)
        else:
            # Regular users see only their logs
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM AuditLogs 
                        WHERE user_id = %s 
                        ORDER BY action_time DESC 
                        LIMIT 20
                    """, (current_user.user_id,))
                    audit_logs = cursor.fetchall()
                conn.close()
            except:
                pass
        
        return render_template('dashboard.html', user=user_data, sessions=sessions, audit_logs=audit_logs)
    
    except Exception as e:
        conn.close()
        return redirect(url_for('auth.login'))

@dashboard_bp.route('/')
def index():
    """Root route - redirect to dashboard if logged in, otherwise login."""
    from flask_login import current_user
    if current_user.is_authenticated:
        from flask import session as flask_session
        if flask_session.get('role') == 'Admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('dashboard.dashboard'))
    else:
        return redirect(url_for('auth.login'))

