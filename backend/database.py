# backend/database.py - PRODUCTION READY VERSION
import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL from environment variable (set in Render)
# This is the secure, modern way to handle secrets
DATABASE_URL = os.environ.get('postgresql://neondb_owner:npg_0NvhHmca2sil@ep-summer-recipe-ajcekgh8-pooler.c-3.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

# If running locally and no environment variable is set, ask the user to provide one.
if DATABASE_URL is None:
    # For local development, you can create a .env file, but for now, we'll prompt.
    # In production (Render), this will be set automatically.
    raise ValueError("No DATABASE_URL environment variable set. Please configure it in your hosting platform.")

def get_db_connection():
    """Create a connection to the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        # Re-raise the exception to stop the app if DB is down
        raise e

def init_database():
    """Create tables if they don't exist"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Sessions table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(200) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Mistakes table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS mistakes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                input_text TEXT NOT NULL,
                analysis TEXT NOT NULL,
                pattern_category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ Cloud database initialized/verified")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise e
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Initialize the database
init_database()

class Database:
    def __init__(self):
        self.conn = get_db_connection()
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    # ===== USER FUNCTIONS =====
    def create_user(self, username, email, password_hash):
        self.cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, password_hash)
        )
        self.conn.commit()
        result = self.cur.fetchone()
        return result['id'] if result else None
    
    def get_user_by_username(self, username):
        self.cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        return self.cur.fetchone()
    
    def get_user_by_email(self, email):
        self.cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return self.cur.fetchone()
    
    def get_user_by_id(self, user_id):
        self.cur.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (user_id,))
        return self.cur.fetchone()
    
    def update_last_login(self, user_id):
        self.cur.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.now(), user_id)
        )
        self.conn.commit()
    
    # ===== SESSION FUNCTIONS =====
    def create_session(self, user_id, token, expires_at):
        self.cur.execute(
            "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
            (user_id, token, expires_at)
        )
        self.conn.commit()
    
    def get_session(self, token):
        self.cur.execute(
            "SELECT * FROM sessions WHERE session_token = %s AND expires_at > %s",
            (token, datetime.now())
        )
        return self.cur.fetchone()
    
    def delete_session(self, token):
        self.cur.execute("DELETE FROM sessions WHERE session_token = %s", (token,))
        self.conn.commit()
    
    def delete_user_sessions(self, user_id):
        self.cur.execute("DELETE FROM sessions WHERE user_id = %s", (user_id,))
        self.conn.commit()
    
    # ===== MISTAKE FUNCTIONS =====
    def save_mistake(self, user_id, input_text, analysis, pattern_category=None):
        analysis_json = json.dumps(analysis)
        self.cur.execute(
            "INSERT INTO mistakes (user_id, input_text, analysis, pattern_category) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, input_text, analysis_json, pattern_category)
        )
        self.conn.commit()
        result = self.cur.fetchone()
        return result['id'] if result else None
    
    def get_user_mistakes(self, user_id, limit=50):
        self.cur.execute(
            "SELECT * FROM mistakes WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )
        return self.cur.fetchall()
    
    def get_mistake_patterns(self, user_id):
        self.cur.execute(
            "SELECT pattern_category, COUNT(*) as count FROM mistakes WHERE user_id = %s AND pattern_category IS NOT NULL GROUP BY pattern_category ORDER BY count DESC",
            (user_id,)
        )
        return self.cur.fetchall()
    
    def get_recent_mistakes(self, user_id, days=7):
        self.cur.execute(
            "SELECT * FROM mistakes WHERE user_id = %s AND created_at >= NOW() - INTERVAL '%s days' ORDER BY created_at DESC",
            (user_id, days)
        )
        return self.cur.fetchall()