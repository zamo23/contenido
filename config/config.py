import os
from dotenv import load_dotenv

load_dotenv('.env')

class Config:
    @staticmethod
    def get_pexels_token():
        return os.getenv('Token_pexels')
    """Configuration class for environment variables."""
    
    @staticmethod
    def get_db_host():
        return os.getenv('DB_HOST')
    
    @staticmethod
    def get_db_user():
        return os.getenv('DB_USER')
    
    @staticmethod
    def get_db_password():
        return os.getenv('DB_PASSWORD')
    
    @staticmethod
    def get_db_name():
        return os.getenv('DB_NAME')
    
    @staticmethod
    def get_db_port():
        return os.getenv('DB_PORT')
    
    @staticmethod
    def get_google_api_key():
        return os.getenv('IA_GOOGLE')
    
    @staticmethod
    def get_telegram_token():
        return os.getenv('token_telegram')
    
    @staticmethod
    def get_notion_token():
        return os.getenv('Token_notion')
    
    @staticmethod
    def get_notion_database_id():
        return os.getenv('NOTION_DATABASE_ID')