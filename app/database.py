import mysql.connector
from mysql.connector import Error
import os

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "3306"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "crm_automation"),
        )
        return conn
    except Error as e:
        print(f"MySQL connection error: {e}")
        raise

def get_db():
    
    return get_connection()
