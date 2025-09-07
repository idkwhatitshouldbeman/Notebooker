"""
Smart Database Manager for Notebooker
Automatically chooses between Supabase (cloud) and SQLite (local)
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartNotebookerDB:
    """Smart database manager that works with both Supabase and SQLite"""
    
    def __init__(self):
        self.use_supabase = False
        self.db_path = "notebooker.db"
        
        # Try to use Supabase if credentials are available
        if self._try_supabase():
            self.use_supabase = True
            logger.info("Using Supabase database")
        else:
            logger.info("Using SQLite database for local development")
            self._init_sqlite()
    
    def _try_supabase(self):
        """Try to initialize Supabase connection"""
        try:
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                return False
            
            # Try to import and test Supabase
            from supabase_config import SupabaseNotebookerDB
            self.supabase_db = SupabaseNotebookerDB()
            return True
            
        except Exception as e:
            logger.warning(f"Supabase not available: {e}")
            return False
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                self.create_tables()
                logger.info("SQLite database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        if self.use_supabase:
            return self.supabase_db.get_connection()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def create_tables(self):
        """Create database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_supabase:
                    # Use Supabase table creation
                    self.supabase_db.create_tables()
                else:
                    # SQLite table creation
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            email TEXT UNIQUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP,
                            preferences TEXT DEFAULT '{}'
                        )
                    ''')
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS en_files (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            filename TEXT NOT NULL,
                            title TEXT,
                            content TEXT,
                            tags TEXT DEFAULT '[]',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS planning_sheets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            en_file_id INTEGER,
                            section_name TEXT,
                            status TEXT DEFAULT 'draft',
                            content TEXT,
                            questions TEXT DEFAULT '[]',
                            decisions TEXT DEFAULT '[]',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id),
                            FOREIGN KEY (en_file_id) REFERENCES en_files (id)
                        )
                    ''')
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS llm_interactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            model_name TEXT,
                            prompt TEXT,
                            response TEXT,
                            tokens_used INTEGER,
                            cost REAL DEFAULT 0.0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')
                    
                    conn.commit()
                    logger.info("SQLite tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def create_user(self, username: str, email: str = None, preferences: Dict = None) -> int:
        """Create a new user"""
        if self.use_supabase:
            return self.supabase_db.create_user(username, email, preferences)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, preferences)
                    VALUES (?, ?, ?)
                ''', (username, email, json.dumps(preferences or {})))
                user_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created user: {username} (ID: {user_id})")
                return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User {username} already exists")
            return self.get_user_by_username(username)['id']
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        if self.use_supabase:
            return self.supabase_db.get_user_by_username(username)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                if row:
                    user = dict(row)
                    user['preferences'] = json.loads(user['preferences'])
                    return user
                return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def create_en_file(self, user_id: int, filename: str, title: str = None, content: str = "", tags: List[str] = None) -> int:
        """Create a new EN file"""
        if self.use_supabase:
            return self.supabase_db.create_en_file(user_id, filename, title, content, tags)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO en_files (user_id, filename, title, content, tags)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, filename, title, content, json.dumps(tags or [])))
                file_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created EN file: {filename} (ID: {file_id})")
                return file_id
        except Exception as e:
            logger.error(f"Failed to create EN file: {e}")
            raise
    
    def get_en_files(self, user_id: int) -> List[Dict]:
        """Get all EN files for a user"""
        if self.use_supabase:
            return self.supabase_db.get_en_files(user_id)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM en_files WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
                rows = cursor.fetchall()
                files = []
                for row in rows:
                    file_dict = dict(row)
                    file_dict['tags'] = json.loads(file_dict['tags'])
                    files.append(file_dict)
                return files
        except Exception as e:
            logger.error(f"Failed to get EN files: {e}")
            return []
    
    def log_llm_interaction(self, user_id: int, model_name: str, prompt: str, response: str, tokens_used: int = 0, cost: float = 0.0):
        """Log an LLM interaction"""
        if self.use_supabase:
            return self.supabase_db.log_llm_interaction(user_id, model_name, prompt, response, tokens_used, cost)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO llm_interactions (user_id, model_name, prompt, response, tokens_used, cost)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, model_name, prompt, response, tokens_used, cost))
                conn.commit()
                logger.info(f"Logged LLM interaction for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log LLM interaction: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        if self.use_supabase:
            return self.supabase_db.get_user_stats(user_id)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count EN files
                cursor.execute('SELECT COUNT(*) FROM en_files WHERE user_id = ?', (user_id,))
                en_files_count = cursor.fetchone()[0]
                
                # Count planning sections
                cursor.execute('SELECT COUNT(*) FROM planning_sheets WHERE user_id = ?', (user_id,))
                planning_sections_count = cursor.fetchone()[0]
                
                # Count LLM interactions
                cursor.execute('SELECT COUNT(*) FROM llm_interactions WHERE user_id = ?', (user_id,))
                llm_interactions_count = cursor.fetchone()[0]
                
                # Total tokens used
                cursor.execute('SELECT SUM(tokens_used) FROM llm_interactions WHERE user_id = ?', (user_id,))
                total_tokens = cursor.fetchone()[0] or 0
                
                return {
                    'en_files_count': en_files_count,
                    'planning_sections_count': planning_sections_count,
                    'llm_interactions_count': llm_interactions_count,
                    'total_tokens_used': total_tokens
                }
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    # Initialize database (will use SQLite locally, Supabase if configured)
    db = SmartNotebookerDB()
    
    # Create a test user
    user_id = db.create_user("testuser", "test@example.com")
    print(f"Created user with ID: {user_id}")
    
    # Create an EN file
    file_id = db.create_en_file(user_id, "test.txt", "Test File", "Test content", ["test"])
    print(f"Created EN file with ID: {file_id}")
    
    # Log an LLM interaction
    db.log_llm_interaction(user_id, "deepseek/deepseek-chat-v3.1:free", "Test prompt", "Test response", 50, 0.0)
    print("Logged LLM interaction")
    
    # Get user stats
    stats = db.get_user_stats(user_id)
    print(f"User stats: {stats}")
    
    print("Smart database test completed!")
