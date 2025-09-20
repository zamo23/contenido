import json
import logging
import re
import google.generativeai as genai
from typing import Dict, Any, List
from config.config import Config

logger = logging.getLogger(__name__)

class AIGenerator:
    """Handles AI content generation using Google Gemini."""
    
    def __init__(self):
        genai.configure(api_key=Config.get_google_api_key())
        self.model = genai.GenerativeModel("gemini-1.5-pro")
    
    def generate_idea(self, category: str, existing_titles: List[str] = None) -> Dict[str, Any]:
        """Generate idea for a category."""
        existing_str = ""
        if existing_titles:
            existing_str = f"Avoid repeating these existing ideas: {', '.join(existing_titles)}. "
        
        prompt = f"""
        Genera una idea de contenido para TikTok en la categoría: {category} (30 a 45 segundos).
        {existing_str}
        Debe tener:
        1. Un título corto.
        2. Un guion dividido en 3 partes: gancho, cuerpo, cierre.
        3. Una lista de hashtags virales para TikTok.
        Devuélvelo en JSON con dos versiones: "es" (español) y "en" (inglés).
        Responde SOLO con el JSON, sin texto adicional.
        Formato exacto:
        {{
          "es": {{
            "title": "Título en español",
            "script": {{
              "gancho": "Gancho en español",
              "cuerpo": "Cuerpo en español",
              "cierre": "Cierre en español"
            }},
            "hashtags": "#Hashtag1 #Hashtag2"
          }},
          "en": {{
            "title": "Title in English",
            "script": {{
              "gancho": "Hook in English",
              "cuerpo": "Body in English",
              "cierre": "Closing in English"
            }},
            "hashtags": "#Hashtag1 #Hashtag2"
          }}
        }}
        """
        
        response = self.model.generate_content(prompt)
        text = response.text.strip()
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_text = text
        
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.error(f"Cleaned JSON text: {json_text}")
            logger.error(f"Response text: {response.text}")
            raise ValueError("AI did not return valid JSON")