import logging
from telegram import Update
from telegram.ext import ContextTypes

from core.tutor import Tutor
from retrieval.vector_store import VectorStoreManager
from retrieval.hybrid_search import HybridSearch
from courses.course_manager import CourseManager
from memory.short_term import ShortTermMemory
from utils.config import config
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Global instances (will be initialized in main.py)
tutor: Tutor = None
vector_manager: VectorStoreManager = None
course_manager: CourseManager = None
hybrid_search: HybridSearch = None
rate_limiter = RateLimiter(config.RATE_LIMIT_REQUESTS, config.RATE_LIMIT_PERIOD)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages from user"""
    
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Rate limiting check
    if not rate_limiter.check(user_id):
        await update.message.reply_text(
            "⏳ شما درخواست‌های زیادی ارسال کرده‌اید. لطفاً چند لحظه صبر کنید."
        )
        return
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Get active course for this user
    active_course = course_manager.get_active_course(user_id)
    
    # Retrieve relevant context from course documents
    context_text = ""
    if active_course:
        # Try hybrid search first
        if hybrid_search:
            results = await hybrid_search.search(
                query=user_message,
                course_name=active_course,
                top_k=config.TOP_K_RETRIEVAL,
            )
        else:
            # Fallback to semantic search only
            results = vector_manager.search(
                query=user_message,
                course_name=active_course,
                top_k=config.TOP_K_RETRIEVAL,
            )
        
        if results:
            context_text = "\n\n---\n\n".join([r["text"] for r in results])
            logger.info(f"Retrieved {len(results)} chunks for user {user_id}")
    
    # Get mode from user data
    mode = context.user_data.get("mode", "qa")
    
    # Generate response
    try:
        response = await tutor.respond(
            user_id=user_id,
            user_message=user_message,
            context=context_text,
            mode=mode,
            course_name=active_course,
        )
        
        # Send response
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in handle_text_message: {e}")
        await update.message.reply_text(
            "❌ خطای داخلی رخ داد. لطفاً دوباره تلاش کنید."
        )


def set_instances(
    t: Tutor,
    vm: VectorStoreManager,
    cm: CourseManager,
    hs: HybridSearch = None,
):
    """Set global instances from main.py"""
    global tutor, vector_manager, course_manager, hybrid_search
    tutor = t
    vector_manager = vm
    course_manager = cm
    hybrid_search = hs