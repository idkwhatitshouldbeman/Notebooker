"""
Cloud Database Management for Notebooker
Works with PostgreSQL on Render, Supabase, or other cloud providers
"""

import os
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudNotebookerDB:
    """PostgreSQL database manager for cloud deployment"""
    
    def __init__(self, database_url: str = None):
        # Get database URL from environment variable (Render sets this automatically)
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        if not self.database_url:
            logger.warning("No DATABASE_URL found. Using local SQLite fallback.")
            self.use_sqlite = True
            self.init_sqlite()
        else:
            self.use_sqlite = False
            self.init_postgresql()
    
    def init_postgresql(self):
        """Initialize PostgreSQL database"""
        try:
            # Parse database URL
            import urllib.parse as urlparse
            url = urlparse.urlparse(self.database_url)
            
            self.conn_params = {
                'host': url.hostname,
                'port': url.port,
                'database': url.path[1:],  # Remove leading slash
                'user': url.username,
                'password': url.password,
                'sslmode': 'require'  # Required for most cloud databases
            }
            
            # Test connection
            with psycopg2.connect(**self.conn_params) as conn:
                logger.info("PostgreSQL connection successful")
            
            # Create tables
            self.create_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            logger.info("Falling back to SQLite")
            self.use_sqlite = True
            self.init_sqlite()
    
    def init_sqlite(self):
        """Fallback to SQLite for local development"""
        import sqlite3
        self.db_path = "notebooker.db"
        with sqlite3.connect(self.db_path) as conn:
            logger.info("Using SQLite for local development")
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        if self.use_sqlite:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            conn = psycopg2.connect(**self.conn_params)
            return conn
    
    def create_tables(self):
        """Create database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_sqlite:
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
                else:
                    # PostgreSQL table creation
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) UNIQUE NOT NULL,
                            email VARCHAR(255) UNIQUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP,
                            preferences JSONB DEFAULT '{}'
                        )
                    ''')
                
                # EN Files table
                if self.use_sqlite:
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
                else:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS en_files (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            filename VARCHAR(255) NOT NULL,
                            title TEXT,
                            content TEXT,
                            tags JSONB DEFAULT '[]',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')
                
                # Planning Sheets table
                if self.use_sqlite:
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
                else:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS planning_sheets (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            en_file_id INTEGER,
                            section_name VARCHAR(255),
                            status VARCHAR(50) DEFAULT 'draft',
                            content TEXT,
                            questions JSONB DEFAULT '[]',
                            decisions JSONB DEFAULT '[]',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id),
                            FOREIGN KEY (en_file_id) REFERENCES en_files (id)
                        )
                    ''')
                
                # LLM Interactions table
                if self.use_sqlite:
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
                else:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS llm_interactions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            model_name VARCHAR(255),
                            prompt TEXT,
                            response TEXT,
                            tokens_used INTEGER,
                            cost DECIMAL(10,4) DEFAULT 0.0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )
                    ''')
                
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def create_user(self, username: str, email: str = None, preferences: Dict = None) -> int:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute('''
                        INSERT INTO users (username, email, preferences)
                        VALUES (?, ?, ?)
                    ''', (username, email, json.dumps(preferences or {})))
                else:
                    cursor.execute('''
                        INSERT INTO users (username, email, preferences)
                        VALUES (%s, %s, %s)
                    ''', (username, email, json.dumps(preferences or {})))
                
                user_id = cursor.lastrowid if self.use_sqlite else cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Created user: {username} (ID: {user_id})")
                return user_id
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor if not self.use_sqlite else None)
                
                if self.use_sqlite:
                    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                    row = cursor.fetchone()
                    if row:
                        user = dict(row)
                        user['preferences'] = json.loads(user['preferences'])
                        return user
                else:
                    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                    row = cursor.fetchone()
                    if row:
                        user = dict(row)
                        if isinstance(user['preferences'], str):
                            user['preferences'] = json.loads(user['preferences'])
                        return user
                return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def create_en_file(self, user_id: int, filename: str, title: str = None, content: str = "", tags: List[str] = None) -> int:
        """Create a new EN file"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute('''
                        INSERT INTO en_files (user_id, filename, title, content, tags)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, filename, title, content, json.dumps(tags or [])))
                    file_id = cursor.lastrowid
                else:
                    cursor.execute('''
                        INSERT INTO en_files (user_id, filename, title, content, tags)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id
                    ''', (user_id, filename, title, content, json.dumps(tags or [])))
                    file_id = cursor.fetchone()[0]
                
                conn.commit()
                logger.info(f"Created EN file: {filename} (ID: {file_id})")
                return file_id
        except Exception as e:
            logger.error(f"Failed to create EN file: {e}")
            raise
    
    def get_en_files(self, user_id: int) -> List[Dict]:
        """Get all EN files for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor if not self.use_sqlite else None)
                
                if self.use_sqlite:
                    cursor.execute('SELECT * FROM en_files WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
                    rows = cursor.fetchall()
                    files = []
                    for row in rows:
                        file_dict = dict(row)
                        file_dict['tags'] = json.loads(file_dict['tags'])
                        files.append(file_dict)
                    return files
                else:
                    cursor.execute('SELECT * FROM en_files WHERE user_id = %s ORDER BY updated_at DESC', (user_id,))
                    rows = cursor.fetchall()
                    files = []
                    for row in rows:
                        file_dict = dict(row)
                        if isinstance(file_dict['tags'], str):
                            file_dict['tags'] = json.loads(file_dict['tags'])
                        files.append(file_dict)
                    return files
        except Exception as e:
            logger.error(f"Failed to get EN files: {e}")
            return []
    
    def log_llm_interaction(self, user_id: int, model_name: str, prompt: str, response: str, tokens_used: int = 0, cost: float = 0.0):
        """Log an LLM interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_sqlite:
                    cursor.execute('''
                        INSERT INTO llm_interactions (user_id, model_name, prompt, response, tokens_used, cost)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, model_name, prompt, response, tokens_used, cost))
                else:
                    cursor.execute('''
                        INSERT INTO llm_interactions (user_id, model_name, prompt, response, tokens_used, cost)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (user_id, model_name, prompt, response, tokens_used, cost))
                
                conn.commit()
                logger.info(f"Logged LLM interaction for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log LLM interaction: {e}")

# Example usage
if __name__ == "__main__":
    # This will automatically use DATABASE_URL if available (on Render)
    # or fall back to SQLite for local development
    db = CloudNotebookerDB()
    
    # Create a test user
    user_id = db.create_user("testuser", "test@example.com")
    print(f"Created user with ID: {user_id}")
    
    # Create an EN file
    file_id = db.create_en_file(user_id, "test.txt", "Test File", "Test content", ["test"])
    print(f"Created EN file with ID: {file_id}")
    
    # Log an LLM interaction
    db.log_llm_interaction(user_id, "deepseek/deepseek-chat-v3.1:free", "Test prompt", "Test response", 50, 0.0)
    print("Logged LLM interaction")
    
    print("Cloud database test completed!")
