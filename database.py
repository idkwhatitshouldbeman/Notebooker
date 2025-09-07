"""
Database Management for Notebooker
Handles user data, EN files, and planning sheets
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotebookerDB:
    """SQLite database manager for Notebooker"""
    
    def __init__(self, db_path: str = "notebooker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
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
                
                # EN Files table
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
                
                # Planning Sheets table
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
                
                # Images table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        en_file_id INTEGER,
                        filename TEXT NOT NULL,
                        original_name TEXT,
                        file_path TEXT,
                        caption TEXT,
                        metadata TEXT DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (en_file_id) REFERENCES en_files (id)
                    )
                ''')
                
                # LLM Interactions table
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
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_user(self, username: str, email: str = None, preferences: Dict = None) -> int:
        """Create a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
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
        try:
            with sqlite3.connect(self.db_path) as conn:
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
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
    
    def update_en_file(self, file_id: int, content: str = None, title: str = None, tags: List[str] = None):
        """Update an EN file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if content is not None:
                    updates.append("content = ?")
                    params.append(content)
                
                if title is not None:
                    updates.append("title = ?")
                    params.append(title)
                
                if tags is not None:
                    updates.append("tags = ?")
                    params.append(json.dumps(tags))
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(file_id)
                
                query = f"UPDATE en_files SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                logger.info(f"Updated EN file ID: {file_id}")
        except Exception as e:
            logger.error(f"Failed to update EN file: {e}")
            raise
    
    def create_planning_section(self, user_id: int, en_file_id: int, section_name: str, content: str = "", questions: List[str] = None, decisions: List[str] = None) -> int:
        """Create a new planning section"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO planning_sheets (user_id, en_file_id, section_name, content, questions, decisions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, en_file_id, section_name, content, json.dumps(questions or []), json.dumps(decisions or [])))
                section_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created planning section: {section_name} (ID: {section_id})")
                return section_id
        except Exception as e:
            logger.error(f"Failed to create planning section: {e}")
            raise
    
    def get_planning_sections(self, user_id: int, en_file_id: int = None) -> List[Dict]:
        """Get planning sections for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if en_file_id:
                    cursor.execute('SELECT * FROM planning_sheets WHERE user_id = ? AND en_file_id = ? ORDER BY created_at DESC', (user_id, en_file_id))
                else:
                    cursor.execute('SELECT * FROM planning_sheets WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
                
                rows = cursor.fetchall()
                sections = []
                for row in rows:
                    section_dict = dict(row)
                    section_dict['questions'] = json.loads(section_dict['questions'])
                    section_dict['decisions'] = json.loads(section_dict['decisions'])
                    sections.append(section_dict)
                return sections
        except Exception as e:
            logger.error(f"Failed to get planning sections: {e}")
            return []
    
    def log_llm_interaction(self, user_id: int, model_name: str, prompt: str, response: str, tokens_used: int = 0, cost: float = 0.0):
        """Log an LLM interaction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
        try:
            with sqlite3.connect(self.db_path) as conn:
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
    
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/notebooker_backup_{timestamp}.db"
        
        try:
            Path("backups").mkdir(exist_ok=True)
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Initialize database
    db = NotebookerDB()
    
    # Create a test user
    user_id = db.create_user("test_user", "test@example.com")
    
    # Create an EN file
    file_id = db.create_en_file(user_id, "test_file.txt", "Test EN File", "This is test content", ["test", "example"])
    
    # Create a planning section
    section_id = db.create_planning_section(user_id, file_id, "Introduction", "This is the introduction section", ["What is the main goal?"], ["Use simple language"])
    
    # Log an LLM interaction
    db.log_llm_interaction(user_id, "deepseek/deepseek-chat-v3.1:free", "Test prompt", "Test response", 50, 0.0)
    
    # Get user stats
    stats = db.get_user_stats(user_id)
    print(f"User stats: {stats}")
    
    print("Database test completed successfully!")
