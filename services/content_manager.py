from typing import Dict, Any
from database.database import DatabaseHandler
from services.ai_generator import AIGenerator

class ContentManager:
    """Manages content operations."""
    
    def __init__(self, db_handler: DatabaseHandler, ai_generator: AIGenerator):
        self.db_handler = db_handler
        self.ai_generator = ai_generator
    
    def generate_and_save_idea(self, user_id: int, category: str) -> Dict[str, Any]:
        """Generate and save idea."""
        existing_ideas = self.db_handler.get_user_ideas(user_id, category)
        existing_titles = list(set(idea['title'] for idea in existing_ideas if 'title' in idea))
        ideas = self.ai_generator.generate_idea(category, existing_titles)
        idea_id = self.db_handler.insert_idea(user_id, category, ideas)
        return ideas