from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import pymysql
from models.user import User
from config import Config
from utils.security import hash_password, verify_password, validate_password_strength
from utils.sessions import create_session
from utils.logging import create_audit_log

auth_bp = Blueprint('auth', __name__)

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

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        # Validate password strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('register.html')
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Check if username or email already exists
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again.', 'danger')
            return render_template('register.html')
        
        try:
            with conn.cursor() as cursor:
                # Check username
                cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already exists!', 'danger')
                    conn.close()
                    return render_template('register.html')
                
                # Check email
                cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email already exists!', 'danger')
                    conn.close()
                    return render_template('register.html')
                
                # Get default role_id (User role)
                cursor.execute("SELECT role_id FROM Roles WHERE role_name = 'User'")
                role = cursor.fetchone()
                role_id = role['role_id'] if role else 1
                
                # Insert new user
                cursor.execute(
                    "INSERT INTO Users (username, email, hashed_password, full_name, role_id) VALUES (%s, %s, %s, %s, %s)",
                    (username, email, hashed_password, full_name, role_id)
                )
                conn.commit()
                
                # Get the new user's ID
                user_id = cursor.lastrowid
                
                # Create audit log
                create_audit_log(user_id, 'User registered')
                
                flash('Registration successful! Please login.', 'success')
                conn.close()
                return redirect(url_for('auth.login'))
        
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            conn.close()
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
        
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again.', 'danger')
            return render_template('login.html')
        
        try:
            with conn.cursor() as cursor:
                # Get user with role
                cursor.execute("""
                    SELECT u.*, r.role_name 
                    FROM Users u 
                    LEFT JOIN Roles r ON u.role_id = r.role_id 
                    WHERE u.username = %s
                """, (username,))
                user_data = cursor.fetchone()
                
                if user_data and verify_password(user_data['hashed_password'], password):
                    # Create User object
                    user = User(
                        user_id=user_data['user_id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['hashed_password'],
                        full_name=user_data.get('full_name'),
                        profile_pic=user_data.get('profile_pic'),
                        role_id=user_data.get('role_id'),
                        created_at=user_data.get('created_at'),
                        updated_at=user_data.get('updated_at')
                    )
                    
                    # Store role in Flask session
                    flask_session['role'] = user_data.get('role_name', 'User')
                    
                    # Login user
                    login_user(user, remember=True)
                    
                    # Create session record
                    ip_address = request.remote_addr
                    user_agent = request.headers.get('User-Agent', '')
                    session_id = create_session(user_data['user_id'], ip_address, user_agent)
                    flask_session['db_session_id'] = session_id
                    
                    # Create audit log
                    create_audit_log(user_data['user_id'], 'User logged in')
                    
                    conn.close()
                    flash('Login successful!', 'success')
                    
                    # Redirect based on role
                    if user_data.get('role_name') == 'Admin':
                        return redirect(url_for('admin.admin_dashboard'))
                    else:
                        return redirect(url_for('dashboard.dashboard'))
                else:
                    flash('Invalid username or password.', 'danger')
                    conn.close()
                    return render_template('login.html')
        
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
            conn.close()
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    user_id = current_user.user_id
    
    # End session
    session_id = flask_session.get('db_session_id')
    if session_id:
        from utils.sessions import end_session
        end_session(session_id)
    
    # Create audit log
    create_audit_log(user_id, 'User logged out')
    
    logout_user()
    flask_session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit user profile."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            
            # Handle profile picture upload
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add user_id to filename to make it unique
                    name, ext = os.path.splitext(filename)
                    filename = f"{current_user.user_id}_{name}{ext}"
                    
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join('static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)
                    
                    # Update database
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "UPDATE Users SET full_name = %s, profile_pic = %s WHERE user_id = %s",
                            (full_name, filename, current_user.user_id)
                        )
                        conn.commit()
                    
                    create_audit_log(current_user.user_id, 'Profile updated')
                    flash('Profile updated successfully!', 'success')
                    conn.close()
                    return redirect(url_for('auth.profile'))
            
            # Update without picture
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE Users SET full_name = %s WHERE user_id = %s",
                    (full_name, current_user.user_id)
                )
                conn.commit()
            
            create_audit_log(current_user.user_id, 'Profile updated')
            flash('Profile updated successfully!', 'success')
            conn.close()
            return redirect(url_for('auth.profile'))
        
        # GET request - show profile
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.role_name 
                FROM Users u 
                LEFT JOIN Roles r ON u.role_id = r.role_id 
                WHERE u.user_id = %s
            """, (current_user.user_id,))
            user_data = cursor.fetchone()
        
        conn.close()
        return render_template('profile.html', user=user_data)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        conn.close()
        return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded profile pictures."""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account."""
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        user_id = current_user.user_id
        
        with conn.cursor() as cursor:
            # Delete user
            cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
            conn.commit()
        
        # Create audit log before logging out
        create_audit_log(user_id, 'Account deleted')
        
        conn.close()
        
        logout_user()
        flask_session.clear()
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('auth.login'))
    
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'danger')
        conn.close()
        return redirect(url_for('dashboard.dashboard'))

