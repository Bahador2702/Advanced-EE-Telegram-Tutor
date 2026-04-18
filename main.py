#!/usr/bin/env python3
import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from utils.config import config
from utils.logger import setup_logging
from core.tutor import Tutor
from core.mode_detector import ModeDetector
from courses.course_manager import CourseManager
from retrieval.vector_store import VectorStoreManager
from retrieval.hybrid_search import HybridSearch
from memory.short_term import ShortTermMemory
from bot.handlers import commands, messages, callbacks
from db.database import init_db

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
tutor = None
course_manager = None
vector_manager = None
hybrid_search = None
short_memory = None


async def post_init(application: Application):
    """Run after bot starts"""
    global tutor, course_manager, vector_manager, hybrid_search, short_memory
    
    logger.info("Initializing bot components...")
    
    # Initialize database
    await init_db()
    
    # Initialize core components
    tutor = Tutor()
    course_manager = CourseManager()
    vector_manager = VectorStoreManager()
    hybrid_search = HybridSearch(vector_manager)
    short_memory = ShortTermMemory()
    
    # Set instances for handlers
    messages.set_instances(tutor, vector_manager, course_manager, hybrid_search)
    callbacks.set_instances(course_manager, tutor)
    
    logger.info("Bot is ready!")


def main():
    """Main entry point"""
    # Validate config
    try:
        config.validate()
        logger.info(config.display())
    except ValueError as e:
        logger.error(f"Config error: {e}")
        return
    
    # Create application
    application = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", commands.start_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("new_course", commands.new_course_command))
    application.add_handler(CommandHandler("courses", commands.courses_command))
    application.add_handler(CommandHandler("course", commands.course_command))
    application.add_handler(CommandHandler("mode", commands.mode_command))
    application.add_handler(CommandHandler("stats", commands.stats_command))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_text_message))
    
    # Add callback handler for inline keyboards
    application.add_handler(CallbackQueryHandler(callbacks.handle_callback))
    
    # Start bot
    logger.info("Starting Telegram Tutor Bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()