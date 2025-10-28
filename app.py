from flask import Flask
from flask_login import LoginManager
from config import Config
from models.user import User
from routes import auth, admin, dashboard
import pymysql
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.role_name 
                FROM Users u 
                LEFT JOIN Roles r ON u.role_id = r.role_id 
                WHERE u.user_id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
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
                connection.close()
                return user
        
        connection.close()
        return None
    
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# Register blueprints
app.register_blueprint(auth.auth_bp)
app.register_blueprint(admin.admin_bp)
app.register_blueprint(dashboard.dashboard_bp)

# Create necessary directories
os.makedirs('static/uploads', exist_ok=True)

if __name__ == '__main__':
    # Check if database tables exist, if not, create them
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
            cursor.execute(f"USE {Config.MYSQL_DB}")
            
            # Create Roles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Roles (
                    role_id INT PRIMARY KEY AUTO_INCREMENT,
                    role_name VARCHAR(50) UNIQUE NOT NULL,
                    description VARCHAR(255)
                )
            """)
            
            # Insert default roles if they don't exist
            cursor.execute("SELECT COUNT(*) as count FROM Roles")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("INSERT INTO Roles (role_name, description) VALUES ('Admin', 'Administrator with full access')")
                cursor.execute("INSERT INTO Roles (role_name, description) VALUES ('User', 'Regular user with limited access')")
            
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    profile_pic VARCHAR(255),
                    role_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (role_id) REFERENCES Roles(role_id)
                )
            """)
            
            # Create Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Sessions (
                    session_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logout_time TIMESTAMP NULL,
                    ip_address VARCHAR(45),
                    user_agent VARCHAR(255),
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                )
            """)
            
            # Create AuditLogs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS AuditLogs (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(100),
                    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                )
            """)
            
            connection.commit()
        
        connection.close()
        print("Database initialized successfully!")
    
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Please make sure MySQL is running and credentials are correct in .env file")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

