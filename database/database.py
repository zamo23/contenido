import json
import logging
import mysql.connector
from mysql.connector import Error
from typing import Dict, Any, List
from config.config import Config

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Handles database connections and operations."""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=Config.get_db_host(),
                user=Config.get_db_user(),
                password=Config.get_db_password(),
                database=Config.get_db_name()
            )
            logger.info("Database connected successfully")
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def check_user_access(self, user_id: int) -> bool:
        """Check if user has access."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    
    def insert_idea(self, user_id: int, category: str, ideas: Dict[str, Any]) -> int:
        """Insert new idea and translations, return idea_id."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO content_ideas (user_id, category) VALUES (%s, %s)", (user_id, category))
        idea_id = cursor.lastrowid
        
        for lang, data in ideas.items():
            content_json = json.dumps(data['script'])
            cursor.execute(
                "INSERT INTO content_translations (idea_id, language, title, content, hashtags) VALUES (%s, %s, %s, %s, %s)",
                (idea_id, lang, data['title'], content_json, data['hashtags'])
            )
        
        self.connection.commit()
        cursor.close()
        return idea_id
    
    def get_user_categories(self, user_id: int) -> List[str]:
        """Get user's categories."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT category FROM content_ideas WHERE user_id = %s ORDER BY category", (user_id,))
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def add_user_category(self, user_id: int, category: str):
        """Add a category for user (by inserting a dummy idea or just ensure exists)."""
        pass
    
    def get_user_ideas(self, user_id: int, category: str = None, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get user's ideas, optionally by category."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor(dictionary=True)
        if category:
            cursor.execute("""
                SELECT i.id, i.category, i.created_at, t.language, t.title, t.content, t.hashtags
                FROM content_ideas i
                JOIN content_translations t ON i.id = t.idea_id
                WHERE i.user_id = %s AND i.category = %s
                ORDER BY i.created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, category, limit, offset))
        else:
            cursor.execute("""
                SELECT i.id, i.category, i.created_at, t.language, t.title, t.content, t.hashtags
                FROM content_ideas i
                JOIN content_translations t ON i.id = t.idea_id
                WHERE i.user_id = %s
                ORDER BY i.created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def update_user_category(self, user_id: int, old_cat: str, new_cat: str):
        """Update category name for user."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE content_ideas SET category = %s WHERE user_id = %s AND category = %s", (new_cat, user_id, old_cat))
        self.connection.commit()
        cursor.close()
    
    def delete_user_category(self, user_id: int, category: str):
        """Delete all ideas in a category for user."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM content_ideas WHERE user_id = %s AND category = %s", (user_id, category))
        self.connection.commit()
        cursor.close()
    
    def get_idea_with_translations(self, idea_id: int) -> Dict[str, Dict]:
        """Get translations for a specific idea."""
        if not self.connection.is_connected():
            self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT language, title, content, hashtags
            FROM content_translations
            WHERE idea_id = %s
        """, (idea_id,))
        results = cursor.fetchall()
        cursor.close()
        translations = {}
        for row in results:
            lang = row['language']
            translations[lang] = {
                'title': row['title'],
                'content': json.loads(row['content']),
                'hashtags': row['hashtags']
            }
        return translations