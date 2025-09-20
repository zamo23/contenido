import asyncio
import logging
from telegram import BotCommand
from config.config import Config
from database.database import DatabaseHandler
from services.ai_generator import AIGenerator
from controllers.access_controller import AccessController
from services.content_manager import ContentManager
from bot.telegram_bot import TelegramBot

def main():
    db_handler = DatabaseHandler()
    ai_generator = AIGenerator()
    access_controller = AccessController(db_handler)
    content_manager = ContentManager(db_handler, ai_generator)
    
    token = Config.get_telegram_token()
    if not token:
        return
    
    bot = TelegramBot(token, access_controller, content_manager)
    
    async def set_commands():
        commands = [
            BotCommand("start", "Verificar acceso"),
            BotCommand("generar", "Generar ideas de contenido"),
            BotCommand("help", "Mostrar esta ayuda")
        ]
        await bot.application.bot.set_my_commands(commands)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_commands())
    print("Bot Funcionando Correctamente ...")
    bot.run()

if __name__ == "__main__":
    main()