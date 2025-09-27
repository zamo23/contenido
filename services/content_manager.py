from typing import Dict, Any
from database.database import DatabaseHandler
from services.ai_generator import AIGenerator
from services.notion_handler import NotionHandler

class ContentManager:
    """Manages content operations."""
    
    def __init__(self, db_handler: DatabaseHandler, ai_generator: AIGenerator):
        self.db_handler = db_handler
        self.ai_generator = ai_generator
        self.notion_handler = NotionHandler()
    
    def generate_and_save_idea(self, user_id: int, category: str) -> Dict[str, Any]:
        """Generate and save idea, and search images/videos with Pexels."""
        from services.pexels_searcher import PexelsSearcher
        existing_ideas = self.db_handler.get_user_ideas(user_id, category)
        existing_titles = list(set(idea['title'] for idea in existing_ideas if 'title' in idea))
        ideas = self.ai_generator.generate_idea(category, existing_titles)
        # Buscar imágenes/videos usando los prompts generados por la IA
        pexels = PexelsSearcher()
        for lang in ['es', 'en']:
            pexels_prompt = ideas.get(lang, {}).get('pexels_prompt', None)
            images = []
            videos = []
            if pexels_prompt:
                images = pexels.search_images(pexels_prompt, per_page=2, orientation='portrait')
                videos = pexels.search_videos(pexels_prompt, per_page=8, orientation='portrait')
            # Guardar los resultados en la idea
            ideas[lang]['pexels_images'] = images
            ideas[lang]['pexels_videos'] = videos
            ideas[lang]['pexels_prompt'] = pexels_prompt
        # Guardar en la base de datos
        idea_id = self.db_handler.insert_idea(user_id, category, ideas)
        # Guardar en Notion
        self.notion_handler.create_content_page(ideas, category)
        return ideas