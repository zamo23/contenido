from database.database import DatabaseHandler

class AccessController:
    """Controls user access."""
    
    def __init__(self, db_handler: DatabaseHandler):
        self.db_handler = db_handler
    
    def has_access(self, user_id: int) -> bool:
        return self.db_handler.check_user_access(user_id)