"""
User Authentication System for Notebooker
Handles login, signup, and session management
"""

import hashlib
import secrets
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database_manager import SmartNotebookerDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, db: SmartNotebookerDB):
        self.db = db
        self.sessions = {}  # In production, use Redis or database
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == password_hash
        except:
            return False
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            # Check if user already exists
            existing_user = self.db.get_user_by_username(username)
            if existing_user:
                return {"success": False, "error": "Username already exists"}
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user in database
            user_id = self.db.create_user(username, email, {"password_hash": password_hash})
            
            # Create session
            session_token = self.create_session(user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "session_token": session_token
            }
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return {"success": False, "error": str(e)}
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and create session"""
        try:
            # Get user from database
            user = self.db.get_user_by_username(username)
            if not user:
                return {"success": False, "error": "Invalid username or password"}
            
            # Verify password
            stored_hash = user.get('preferences', {}).get('password_hash')
            if not stored_hash or not self.verify_password(password, stored_hash):
                return {"success": False, "error": "Invalid username or password"}
            
            # Create session
            session_token = self.create_session(user['id'])
            
            # Update last login
            self.update_last_login(user['id'])
            
            return {
                "success": True,
                "user_id": user['id'],
                "username": user['username'],
                "session_token": session_token
            }
        except Exception as e:
            logger.error(f"Failed to login user: {e}")
            return {"success": False, "error": str(e)}
    
    def create_session(self, user_id: int) -> str:
        """Create a new session for user"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)  # 30-day session
        
        self.sessions[session_token] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": expires_at
        }
        
        logger.info(f"Created session for user {user_id}")
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user info"""
        if not session_token or session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Check if session expired
        if datetime.now() > session['expires_at']:
            del self.sessions[session_token]
            return None
        
        # Get user info by ID
        user = self.get_user_by_id(session['user_id'])
        if not user:
            del self.sessions[session_token]
            return None
        
        return {
            "user_id": user['id'],
            "username": user['username'],
            "email": user['email']
        }
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user and invalidate session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            logger.info("User logged out")
            return True
        return False
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        try:
            # Get user
            user = self.db.get_user_by_username(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Verify old password
            stored_hash = user.get('preferences', {}).get('password_hash')
            if not self.verify_password(old_password, stored_hash):
                return {"success": False, "error": "Invalid current password"}
            
            # Hash new password
            new_hash = self.hash_password(new_password)
            
            # Update password
            preferences = user['preferences']
            preferences['password_hash'] = new_hash
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET preferences = ? WHERE id = ?
                ''', (json.dumps(preferences), user_id))
                conn.commit()
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to change password: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                row = cursor.fetchone()
                if row:
                    user = dict(row)
                    if isinstance(user.get('preferences'), str):
                        user['preferences'] = json.loads(user['preferences'])
                    return user
                return None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

# Example usage
if __name__ == "__main__":
    from database_manager import SmartNotebookerDB
    
    # Initialize database and auth
    db = SmartNotebookerDB()
    auth = AuthManager(db)
    
    # Create a test user
    result = auth.create_user("testuser", "test@example.com", "password123")
    print(f"Create user result: {result}")
    
    # Login user
    login_result = auth.login_user("testuser", "password123")
    print(f"Login result: {login_result}")
    
    # Validate session
    if login_result['success']:
        session_token = login_result['session_token']
        user_info = auth.validate_session(session_token)
        print(f"Session validation: {user_info}")
    
    print("Authentication test completed!")
