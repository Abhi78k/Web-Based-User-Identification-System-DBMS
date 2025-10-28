from config import Config
import pymysql
from datetime import datetime

def create_session(user_id, ip_address, user_agent):
    """Create a new session record in the database."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO Sessions (user_id, ip_address, user_agent, login_time) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (user_id, ip_address, user_agent, datetime.now()))
            connection.commit()
            session_id = cursor.lastrowid
        
        connection.close()
        return session_id
    except Exception as e:
        print(f"Error creating session: {e}")
        return None

def end_session(session_id):
    """Update session with logout time."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = "UPDATE Sessions SET logout_time = %s WHERE session_id = %s"
            cursor.execute(sql, (datetime.now(), session_id))
            connection.commit()
        
        connection.close()
        return True
    except Exception as e:
        print(f"Error ending session: {e}")
        return False

def get_user_sessions(user_id, limit=10):
    """Get user's session history."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = """SELECT * FROM Sessions 
                     WHERE user_id = %s 
                     ORDER BY login_time DESC 
                     LIMIT %s"""
            cursor.execute(sql, (user_id, limit))
            results = cursor.fetchall()
        
        connection.close()
        return results
    except Exception as e:
        print(f"Error getting user sessions: {e}")
        return []

def get_all_sessions(limit=100):
    """Get all sessions (for admin)."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = """SELECT s.*, u.username 
                     FROM Sessions s
                     LEFT JOIN Users u ON s.user_id = u.user_id 
                     ORDER BY s.login_time DESC 
                     LIMIT %s"""
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()
        
        connection.close()
        return results
    except Exception as e:
        print(f"Error getting all sessions: {e}")
        return []

