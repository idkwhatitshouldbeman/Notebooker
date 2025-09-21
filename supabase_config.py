"""
Supabase Configuration for Notebooker
Secure database connection with environment variables
"""

import os
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseNotebookerDB:
    """Supabase PostgreSQL database manager"""
    
    def __init__(self):
        # Get Supabase credentials from environment variables
        self.supabase_url = os.environ.get('SUPABASE_URL', 'https://kqwwwmhuczwksraysvpp.supabase.co')
        self.supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not self.supabase_key:
            logger.error("SUPABASE_KEY environment variable not set!")
            raise ValueError("SUPABASE_KEY is required")
        
        # Parse Supabase URL to get database connection details
        self.db_params = self._parse_supabase_url()
        self.init_database()
    
    def _parse_supabase_url(self):
        """Parse Supabase URL to get database connection parameters"""
        # Extract project reference from Supabase URL
        # URL format: https://[project-ref].supabase.co
        project_ref = self.supabase_url.split('//')[1].split('.')[0]
        
        # Supabase database connection parameters
        return {
            'host': f'db.{project_ref}.supabase.co',
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': self.supabase_key,
            'sslmode': 'require'
        }
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            # Test connection
            with psycopg2.connect(**self.db_params) as conn:
                logger.info("Supabase PostgreSQL connection successful")
            
            # Create tables
            self.create_tables()
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_params)
    
    def create_tables(self):
        """Create database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
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
                
                # Images table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS images (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        en_file_id INTEGER,
                        filename VARCHAR(255) NOT NULL,
                        original_name VARCHAR(255),
                        file_path TEXT,
                        caption TEXT,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (en_file_id) REFERENCES en_files (id)
                    )
                ''')
                
                # LLM Interactions table
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
                logger.info("Supabase database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def create_user(self, username: str, email: str = None, preferences: Dict = None) -> int:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, preferences)
                    VALUES (%s, %s, %s) RETURNING id
                ''', (username, email, json.dumps(preferences or {})))
                user_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Created user: {username} (ID: {user_id})")
                return user_id
        except psycopg2.IntegrityError:
            logger.warning(f"User {username} already exists")
            return self.get_user_by_username(username)['id']
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
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
                cursor = conn.cursor(cursor_factory=RealDictCursor)
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
    
    def update_en_file(self, file_id: int, content: str = None, title: str = None, tags: List[str] = None):
        """Update an EN file"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if content is not None:
                    updates.append("content = %s")
                    params.append(content)
                
                if title is not None:
                    updates.append("title = %s")
                    params.append(title)
                
                if tags is not None:
                    updates.append("tags = %s")
                    params.append(json.dumps(tags))
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(file_id)
                
                query = f"UPDATE en_files SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(query, params)
                conn.commit()
                logger.info(f"Updated EN file ID: {file_id}")
        except Exception as e:
            logger.error(f"Failed to update EN file: {e}")
            raise
    
    def create_planning_section(self, user_id: int, en_file_id: int, section_name: str, content: str = "", questions: List[str] = None, decisions: List[str] = None) -> int:
        """Create a new planning section"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO planning_sheets (user_id, en_file_id, section_name, content, questions, decisions)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                ''', (user_id, en_file_id, section_name, content, json.dumps(questions or []), json.dumps(decisions or [])))
                section_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Created planning section: {section_name} (ID: {section_id})")
                return section_id
        except Exception as e:
            logger.error(f"Failed to create planning section: {e}")
            raise
    
    def get_planning_sections(self, user_id: int, en_file_id: int = None) -> List[Dict]:
        """Get planning sections for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                if en_file_id:
                    cursor.execute('SELECT * FROM planning_sheets WHERE user_id = %s AND en_file_id = %s ORDER BY created_at DESC', (user_id, en_file_id))
                else:
                    cursor.execute('SELECT * FROM planning_sheets WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
                
                rows = cursor.fetchall()
                sections = []
                for row in rows:
                    section_dict = dict(row)
                    if isinstance(section_dict['questions'], str):
                        section_dict['questions'] = json.loads(section_dict['questions'])
                    if isinstance(section_dict['decisions'], str):
                        section_dict['decisions'] = json.loads(section_dict['decisions'])
                    sections.append(section_dict)
                return sections
        except Exception as e:
            logger.error(f"Failed to get planning sections: {e}")
            return []
    
    def log_llm_interaction(self, user_id: int, model_name: str, prompt: str, response: str, tokens_used: int = 0, cost: float = 0.0):
        """Log an LLM interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO llm_interactions (user_id, model_name, prompt, response, tokens_used, cost)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (user_id, model_name, prompt, response, tokens_used, cost))
                conn.commit()
                logger.info(f"Logged LLM interaction for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log LLM interaction: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count EN files
                cursor.execute('SELECT COUNT(*) FROM en_files WHERE user_id = %s', (user_id,))
                en_files_count = cursor.fetchone()[0]
                
                # Count planning sections
                cursor.execute('SELECT COUNT(*) FROM planning_sheets WHERE user_id = %s', (user_id,))
                planning_sections_count = cursor.fetchone()[0]
                
                # Count LLM interactions
                cursor.execute('SELECT COUNT(*) FROM llm_interactions WHERE user_id = %s', (user_id,))
                llm_interactions_count = cursor.fetchone()[0]
                
                # Total tokens used
                cursor.execute('SELECT SUM(tokens_used) FROM llm_interactions WHERE user_id = %s', (user_id,))
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
    # Set environment variables for testing
    import os
    os.environ['SUPABASE_URL'] = 'https://kqwwwmhuczwksraysvpp.supabase.co'
    os.environ['SUPABASE_KEY'] = 'snJrAKpW4jqAuzUa'
    
    # Initialize database
    db = SupabaseNotebookerDB()
    
    # Create a test user
    user_id = db.create_user("testuser", "test@example.com")
    print(f"Created user with ID: {user_id}")
    
    # Create an EN file
    file_id = db.create_en_file(user_id, "test.txt", "Test File", "Test content", ["test"])
    print(f"Created EN file with ID: {file_id}")
    
    # Log an LLM interaction
    db.log_llm_interaction(user_id, "deepseek/deepseek-chat-v3.1:free", "Test prompt", "Test response", 50, 0.0)
    print("Logged LLM interaction")
    
    print("Supabase database test completed!")
