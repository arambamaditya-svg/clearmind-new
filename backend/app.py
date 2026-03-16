# backend/app.py - COMPLETE UPDATED VERSION
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta  # UPDATED
import hashlib  # NEW
import secrets  # NEW
# backend/app.py - Add this at the top after imports
import sys
import os
# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .ai_brain import ai_brain
from database import Database  # NEW

app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
CORS(app)

# ===== NEW: Database initialization =====
db = Database()

# ===== NEW: Helper functions =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_hex(32)

# ===== DATA STORAGE (keep this for backward compatibility) =====
DATA_FOLDER = "student_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ===== ROUTES =====
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/log.html')
def serve_log():
    return send_from_directory('../frontend', 'log.html')

@app.route('/dashboard.html')
def serve_dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# ===== NEW: AUTHENTICATION ENDPOINTS =====
@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({"success": False, "error": "All fields required"}), 400
        
        # Check if user exists
        if db.get_user_by_username(username):
            return jsonify({"success": False, "error": "Username already taken"}), 400
        
        if db.get_user_by_email(email):
            return jsonify({"success": False, "error": "Email already registered"}), 400
        
        # Create user
        password_hash = hash_password(password)
        user_id = db.create_user(username, email, password_hash)
        
        if not user_id:
            return jsonify({"success": False, "error": "Registration failed"}), 500
        
        # Create session
        token = generate_token()
        expires_at = datetime.now() + timedelta(days=30)
        db.create_session(user_id, token, expires_at)
        
        return jsonify({
            "success": True,
            "user": {
                "id": user_id,
                "username": username,
                "email": email
            },
            "token": token
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({"success": False, "error": "Username and password required"}), 400
        
        # Get user
        user = db.get_user_by_username(username)
        if not user:
            return jsonify({"success": False, "error": "Invalid username or password"}), 401
        
        # Check password
        password_hash = hash_password(password)
        if password_hash != user['password_hash']:
            return jsonify({"success": False, "error": "Invalid username or password"}), 401
        
        # Delete old sessions
        db.delete_user_sessions(user['id'])
        
        # Create new session
        token = generate_token()
        expires_at = datetime.now() + timedelta(days=30)
        db.create_session(user['id'], token, expires_at)
        
        # Update last login
        db.update_last_login(user['id'])
        
        return jsonify({
            "success": True,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            },
            "token": token
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            db.delete_session(token)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/me', methods=['GET'])
def get_current_user():
    """Get current user from token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"success": False, "error": "No token"}), 401
        
        session = db.get_session(token)
        if not session:
            return jsonify({"success": False, "error": "Invalid or expired session"}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 401
        
        return jsonify({
            "success": True,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ===== UPDATED: YOUR EXISTING ANALYZE ENDPOINT =====
@app.route('/api/analyze', methods=['POST'])
def analyze_mistake():
    try:
        data = request.json
        student_input = data.get('text', '').strip()
        
        # Get user from token (optional - if not logged in, use anonymous)
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = None
        if token:
            session = db.get_session(token)
            if session:
                user_id = session['user_id']
        
        if not student_input:
            return jsonify({"success": False, "error": "No input"}), 400
        
        print(f"\n📨: {student_input[:50]}...")
        analysis = ai_brain.process(student_input)
        
        # Save to database if user is logged in
        if user_id:
            pattern = analysis.get('pattern_category', analysis.get('error_type', 'unknown'))
            db.save_mistake(user_id, student_input, analysis, pattern)
        
        return jsonify({"success": True, "analysis": analysis})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ===== NEW: User history endpoints =====
@app.route('/api/history', methods=['GET'])
def get_user_history():
    """Get user's mistake history"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"success": False, "error": "Not logged in"}), 401
        
        session = db.get_session(token)
        if not session:
            return jsonify({"success": False, "error": "Invalid session"}), 401
        
        mistakes = db.get_user_mistakes(session['user_id'])
        
        # Format for frontend
        history = []
        for m in mistakes:
            history.append({
                "id": m['id'],
                "input": m['input_text'],
                "analysis": json.loads(m['analysis']),
                "date": m['created_at']
            })
        
        return jsonify({"success": True, "history": history})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    """Get user's mistake patterns"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"success": False, "error": "Not logged in"}), 401
        
        session = db.get_session(token)
        if not session:
            return jsonify({"success": False, "error": "Invalid session"}), 401
        
        patterns = db.get_mistake_patterns(session['user_id'])
        recent = db.get_recent_mistakes(session['user_id'])
        
        return jsonify({
            "success": True,
            "patterns": [{"category": p['pattern_category'], "count": p['count']} for p in patterns],
            "recent_count": len(recent)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ===== START SERVER =====
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 ClearMind Server Starting...")
    print("📁 Models:")
    print("   M1: Trinity Large (Extractor)")
    print("   M2: Trinity Mini (Reasoner)")
    print("   M3: Nemotron Nano (Explainer)")
    print("=" * 50)
    print("📍 http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')