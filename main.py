# main.py

import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot.handlers.commands import (
    start_command, help_command, new_course_command, courses_command,
    course_command, delete_course_command, upload_command, files_command,
    delete_file_command, mode_command, hint_command, quiz_command,
    flashcards_command, summarize_command, study_plan_command,
    reset_session_command, stats_command, debug_retrieval_command,
    voice_command, retry_command, menu_command
)
from bot.handlers.messages import handle_text_message
# from bot.handlers.images import handle_image
# from bot.handlers.voice import handle_voice
# from bot.handlers.callbacks import handle_callback
from utils.config import config
from db.database import init_db

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    """Run after bot starts"""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Telegram Tutor Bot started!")

def main():
    # Validate config
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Config validation failed: {e}")
        return
    
    # Create application
    application = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new_course", new_course_command))
    application.add_handler(CommandHandler("courses", courses_command))
    application.add_handler(CommandHandler("course", course_command))
    application.add_handler(CommandHandler("delete_course", delete_course_command))
    application.add_handler(CommandHandler("upload", upload_command))
    application.add_handler(CommandHandler("files", files_command))
    application.add_handler(CommandHandler("delete_file", delete_file_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("hint", hint_command))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("flashcards", flashcards_command))
    application.add_handler(CommandHandler("summarize", summarize_command))
    application.add_handler(CommandHandler("study_plan", study_plan_command))
    application.add_handler(CommandHandler("reset_session", reset_session_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("debug_retrieval", debug_retrieval_command))
    application.add_handler(CommandHandler("voice", voice_command))
    application.add_handler(CommandHandler("retry", retry_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    # application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    # application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.Document.ALL, upload_command))
    
    # Callback handler
    # application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Start bot
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
