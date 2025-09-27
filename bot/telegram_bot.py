import asyncio
import logging
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from controllers.access_controller import AccessController
from services.content_manager import ContentManager
from config.config import Config

logger = logging.getLogger(__name__)

class TelegramBot:
    """Main bot class."""
    
    def __init__(self, token: str, access_controller: AccessController, content_manager: ContentManager):
        self.token = token
        self.access_controller = access_controller
        self.content_manager = content_manager
        self.application = Application.builder().token(token).build()
        self.user_states = {}  
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("generar", self.generar))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.access_controller.has_access(user_id):
            await update.message.reply_text("❌ No tienes acceso para usar este bot.\nComunícate con el desarrollador.")
            return
        
        keyboard = [
            [InlineKeyboardButton("Gestionar categorías", callback_data="manage_cat")],
            [InlineKeyboardButton("Generar ideas", callback_data="generate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Bienvenido! Elige una opción:", reply_markup=reply_markup)
    
    async def generar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not self.access_controller.has_access(user_id):
            await update.message.reply_text("❌ No tienes acceso para usar este bot.\nComunícate con el desarrollador.")
            return
        
        categories = self.content_manager.db_handler.get_user_categories(user_id)
        if not categories:
            await update.message.reply_text("No tienes categorías. Gestiona tus categorías primero con /start.")
            return
        
        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"gen_cat_{i}")] for i, cat in enumerate(categories)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Selecciona una categoría para generar una idea:", reply_markup=reply_markup)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
        Comandos disponibles:
        /start - Verificar acceso
        /generar - Generar 4 ideas de contenido
        /help - Mostrar esta ayuda
        """
        await update.message.reply_text(help_text)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass 
        
        user_id = query.from_user.id
        
        if not self.access_controller.has_access(user_id):
            try:
                await query.edit_message_text("❌ No tienes acceso para usar este bot.\nComunícate con el desarrollador.")
            except Exception:
                pass
            return
        
        data = query.data
        if data == "manage_cat":
            keyboard = [
                [InlineKeyboardButton("Agregar categoría", callback_data="add_cat")],
                [InlineKeyboardButton("Listar categorías", callback_data="list_cat_0")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text("Gestionar categorías:", reply_markup=reply_markup)
            except Exception:
                pass
        
        elif data == "generate":
            categories = self.content_manager.db_handler.get_user_categories(user_id)
            if not categories:
                try:
                    await query.edit_message_text("No tienes categorías. Gestiona tus categorías primero con /start.")
                except Exception:
                    pass
                return
            
            keyboard = [
                [InlineKeyboardButton(cat, callback_data=f"gen_cat_{i}")] for i, cat in enumerate(categories)
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text("Selecciona una categoría para generar una idea:", reply_markup=reply_markup)
            except Exception:
                pass
        
        elif data == "add_cat":
            self.user_states[user_id] = 'waiting_category_name'
            try:
                await query.edit_message_text("Envía el nombre de la nueva categoría:")
            except Exception:
                pass
        
        elif data.startswith("list_cat_"):
            page = int(data.split("_")[2])
            categories = self.content_manager.db_handler.get_user_categories(user_id)
            if not categories:
                await query.edit_message_text("No tienes categorías.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data="back_main")]]))
                return
            per_page = 5
            start = page * per_page
            end = start + per_page
            page_cats = categories[start:end]
            keyboard = [
                [InlineKeyboardButton(cat, callback_data=f"view_cat_{cat.replace(' ', '_')}_0")] for cat in page_cats
            ]
            if page > 0:
                keyboard.append([InlineKeyboardButton("⬅️ Anterior", callback_data=f"list_cat_{page-1}")])
            if end < len(categories):
                keyboard.append([InlineKeyboardButton("Siguiente ➡️", callback_data=f"list_cat_{page+1}")])
            keyboard.append([InlineKeyboardButton("⬅️ Volver", callback_data="back_main")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Tus categorías:", reply_markup=reply_markup)
        
        elif data.startswith("view_cat_"):
            parts = data.split("_")
            category = "_".join(parts[2:-1]).replace("_", " ")
            page = int(parts[-1])
            keyboard = [
                [InlineKeyboardButton("Ver ideas", callback_data=f"list_ideas_{category.replace(' ', '_')}_0")],
                [InlineKeyboardButton("Editar categoría", callback_data=f"edit_cat_{category.replace(' ', '_')}")],
                [InlineKeyboardButton("Eliminar categoría", callback_data=f"delete_cat_{category.replace(' ', '_')}")]
            ]
            keyboard.append([InlineKeyboardButton("⬅️ Volver", callback_data="list_cat_0")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Categoría: {category}", reply_markup=reply_markup)
        
        elif data.startswith("list_ideas_"):
            parts = data.split("_")
            category = "_".join(parts[2:-1]).replace("_", " ")
            page = int(parts[-1])
            ideas = self.content_manager.db_handler.get_user_ideas(user_id, category, limit=5, offset=page*5)
            if not ideas:
                await query.edit_message_text(f"No hay ideas en '{category}'.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data=f"view_cat_{category.replace(' ', '_')}_0")]]))
                return
            idea_dict = {}
            for idea in ideas:
                iid = idea['id']
                if iid not in idea_dict:
                    idea_dict[iid] = {'es': {}, 'en': {}, 'created_at': idea['created_at']}
                idea_dict[iid][idea['language']] = {
                    'title': idea['title'],
                    'content': idea['content'],
                    'hashtags': idea['hashtags']
                }
            keyboard = []
            for iid, data in list(idea_dict.items())[:5]: 
                title = data.get('es', {}).get('title', 'Sin título')
                date_str = data['created_at'].strftime('%Y-%m-%d')
                keyboard.append([InlineKeyboardButton(f"{title} - {date_str}", callback_data=f"show_idea_{iid}")])
            if page > 0:
                keyboard.append([InlineKeyboardButton("⬅️ Anterior", callback_data=f"list_ideas_{category.replace(' ', '_')}_{page-1}")])
            if len(idea_dict) == 5:
                keyboard.append([InlineKeyboardButton("Siguiente ➡️", callback_data=f"list_ideas_{category.replace(' ', '_')}_{page+1}")])
            keyboard.append([InlineKeyboardButton("⬅️ Volver", callback_data=f"view_cat_{category.replace(' ', '_')}_0")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Ideas en '{category}':", reply_markup=reply_markup)
        
        elif data.startswith("edit_cat_"):
            category = "_".join(data.split("_")[2:]).replace("_", " ")
            self.user_states[user_id] = f'waiting_new_cat_name_{category.replace(" ", "_")}'
            await query.edit_message_text(f"Envía el nuevo nombre para la categoría '{category}':")
        
        elif data.startswith("delete_cat_"):
            category = "_".join(data.split("_")[2:]).replace("_", " ")
            keyboard = [
                [InlineKeyboardButton("Sí, eliminar", callback_data=f"confirm_delete_{category.replace(' ', '_')}")],
                [InlineKeyboardButton("No, cancelar", callback_data=f"view_cat_{category.replace(' ', '_')}_0")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"¿Estás seguro de eliminar la categoría '{category}' y todas sus ideas?", reply_markup=reply_markup)
        
        elif data.startswith("confirm_delete_"):
            category = "_".join(data.split("_")[2:]).replace("_", " ")
            self.content_manager.db_handler.delete_user_category(user_id, category)
            await query.edit_message_text(f"Categoría '{category}' eliminada.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data="list_cat_0")]]))
        
        elif data.startswith("show_idea_"):
            iid = int(data.split("_")[2])
            translations = self.content_manager.db_handler.get_idea_with_translations(iid)
            if not translations:
                try:
                    await query.edit_message_text("Idea no encontrada.")
                except Exception:
                    pass
                return
            es = translations.get('es')
            en = translations.get('en')
            try:
                await query.edit_message_text("Mostrando idea...")
            except Exception:
                pass
            if es:
                es_content = f"**{es['title']}**\n\n**Gancho:** {es['content']['gancho']}\n**Cuerpo:** {es['content']['cuerpo']}\n**Cierre:** {es['content']['cierre']}"
                await query.message.reply_text(es_content, parse_mode='Markdown')
                await query.message.reply_text(f"**Hashtags:** {es['hashtags']}", parse_mode='Markdown')
                if 'video_prompts' in es and es['video_prompts']:
                    await query.message.reply_text("**Prompts para videos (Español):**", parse_mode='Markdown')
                    for prompt in es['video_prompts']:
                        await query.message.reply_text(prompt)
            if en:
                en_content = f"**{en['title']}**\n\n**Hook:** {en['content']['gancho']}\n**Body:** {en['content']['cuerpo']}\n**Closing:** {en['content']['cierre']}"
                await query.message.reply_text(en_content, parse_mode='Markdown')
                await query.message.reply_text(f"**Hashtags:** {en['hashtags']}", parse_mode='Markdown')
                if 'video_prompts' in en and en['video_prompts']:
                    await query.message.reply_text("**Prompts para videos (English):**", parse_mode='Markdown')
                    for prompt in en['video_prompts']:
                        await query.message.reply_text(prompt)
        
        elif data.startswith("gen_cat_"):
            cat_index = int(data.split("_")[2])
            categories = self.content_manager.db_handler.get_user_categories(user_id)
            if cat_index >= len(categories):
                try:
                    await query.edit_message_text("Categoría no válida.")
                except Exception:
                    pass
                return
            category = categories[cat_index]
            await query.message.delete()
            generating_msg = await context.bot.send_message(chat_id=query.message.chat_id, text="Estoy generando la idea...")
            try:
                ideas = self.content_manager.generate_and_save_idea(user_id, category)
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=generating_msg.message_id)
                es = ideas['es']
                en = ideas['en']
                es_content = f"**{category} - Español**\n\n**Título:** {es['title']}\n\n**Guion:**\n- Gancho: {es['script']['gancho']}\n- Cuerpo: {es['script']['cuerpo']}\n- Cierre: {es['script']['cierre']}"
                await context.bot.send_message(chat_id=query.message.chat_id, text=es_content, parse_mode='Markdown')
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"**Hashtags:** {es['hashtags']}", parse_mode='Markdown')
                if 'video_prompts' in es and es['video_prompts']:
                    await context.bot.send_message(chat_id=query.message.chat_id, text="**Prompts para videos (Español):**", parse_mode='Markdown')
                    for prompt in es['video_prompts']:
                        await context.bot.send_message(chat_id=query.message.chat_id, text=prompt)
                # Mostrar links de imágenes y videos de Pexels (Español)
                if 'pexels_images' in es and es['pexels_images']:
                    await context.bot.send_message(chat_id=query.message.chat_id, text="**Imágenes sugeridas (Pexels):**", parse_mode='Markdown')
                    for img_url in es['pexels_images']:
                        await context.bot.send_message(chat_id=query.message.chat_id, text=img_url)
                if 'pexels_videos' in es and es['pexels_videos']:
                    await context.bot.send_message(chat_id=query.message.chat_id, text="**Videos sugeridos (Pexels):**", parse_mode='Markdown')
                    for vid_url in es['pexels_videos']:
                        await context.bot.send_message(chat_id=query.message.chat_id, text=vid_url)

                # Usar las claves correctas en inglés
                en_script = en.get('script', {})
                en_content = f"**{category} - English**\n\n**Title:** {en['title']}\n\n**Script:**\n- Hook: {en_script.get('hook', '')}\n- Body: {en_script.get('body', '')}\n- Closing: {en_script.get('closing', '')}"
                await context.bot.send_message(chat_id=query.message.chat_id, text=en_content, parse_mode='Markdown')
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"**Hashtags:** {en['hashtags']}", parse_mode='Markdown')
                if 'video_prompts' in en and en['video_prompts']:
                    await context.bot.send_message(chat_id=query.message.chat_id, text="**Prompts para videos (English):**", parse_mode='Markdown')
                    for prompt in en['video_prompts']:
                        await context.bot.send_message(chat_id=query.message.chat_id, text=prompt)
                # Mostrar links de imágenes y videos de Pexels (Inglés)
                if 'pexels_images' in en and en['pexels_images']:
                    await context.bot.send_message(chat_id=query.message.chat_id, text="**Suggested images (Pexels):**", parse_mode='Markdown')
                    for img_url in en['pexels_images']:
                        await context.bot.send_message(chat_id=query.message.chat_id, text=img_url)
                if 'pexels_videos' in en and en['pexels_videos']:
                    await context.bot.send_message(chat_id=query.message.chat_id, text="**Suggested videos (Pexels):**", parse_mode='Markdown')
                    for vid_url in en['pexels_videos']:
                        await context.bot.send_message(chat_id=query.message.chat_id, text=vid_url)
            except Exception as e:
                await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=generating_msg.message_id, text="Error al generar la idea. Inténtalo de nuevo.")
                logger.error(f"Error generating idea: {e}")
        
        elif data == "back_main":
            keyboard = [
                [InlineKeyboardButton("Gestionar categorías", callback_data="manage_cat")],
                [InlineKeyboardButton("Generar ideas", callback_data="generate")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Bienvenido! Elige una opción:", reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.user_states:
            return
        state = self.user_states[user_id]
        if state == 'waiting_category_name':
            category_name = update.message.text.strip()
            if not category_name:
                await update.message.reply_text("Nombre inválido. Intenta de nuevo:")
                return
            self.content_manager.db_handler.add_user_category(user_id, category_name)
            await update.message.reply_text(f"Categoría '{category_name}' agregada. Ahora puedes generar ideas en ella.")
            del self.user_states[user_id]
            keyboard = [
                [InlineKeyboardButton("Gestionar categorías", callback_data="manage_cat")],
                [InlineKeyboardButton("Generar ideas", callback_data="generate")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Elige una opción:", reply_markup=reply_markup)
        
        elif state.startswith('waiting_new_cat_name_'):
            old_cat = state.split('_', 4)[-1].replace("_", " ")
            new_cat = update.message.text.strip()
            if not new_cat:
                await update.message.reply_text("Nombre inválido. Intenta de nuevo:")
                return
            self.content_manager.db_handler.update_user_category(user_id, old_cat, new_cat)
            await update.message.reply_text(f"Categoría cambiada de '{old_cat}' a '{new_cat}'.")
            del self.user_states[user_id]
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Volver a categorías", callback_data="list_cat_0")]])
            await update.message.reply_text("Categoría actualizada.", reply_markup=reply_markup)
    
    def run(self):
        self.application.run_polling()