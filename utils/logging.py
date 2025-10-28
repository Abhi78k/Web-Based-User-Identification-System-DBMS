from config import Config
import pymysql
from datetime import datetime

def create_audit_log(user_id, action):
    """Create an audit log entry in the database."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO AuditLogs (user_id, action, action_time) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user_id, action, datetime.now()))
            connection.commit()
        
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating audit log: {e}")
        return False

def get_audit_logs(limit=100):
    """Retrieve recent audit logs."""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            sql = """SELECT al.*, u.username 
                     FROM AuditLogs al 
                     LEFT JOIN Users u ON al.user_id = u.user_id 
                     ORDER BY al.action_time DESC 
                     LIMIT %s"""
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()
        
        connection.close()
        return results
    except Exception as e:
        print(f"Error getting audit logs: {e}")
        return []

