import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.database import async_session
from db.models import User, Course, ConversationMessage
from sqlalchemy.future import select
from core.tutor import Tutor
from retrieval.vector_store import VectorStore
from utils.config import config

logger = logging.getLogger(__name__)
tutor = Tutor()

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    async with async_session() as session:
        # Get User and Active Course
        q = select(User).where(User.telegram_id == user_id)
        res = await session.execute(q)
        user = res.scalar_one_or_none()
        
        if not user:
            return # Should not happen with start command
            
        # Last active course (simplified logic)
        q = select(Course).where(Course.user_id == user.id).order_by(Course.last_active.desc())
        res = await session.execute(q)
        active_course = res.scalar_one_or_none()
        
        # Get History
        q = select(ConversationMessage).where(ConversationMessage.user_id == user.id).order_by(ConversationMessage.timestamp.desc()).limit(10)
        res = await session.execute(q)
        history_objs = res.scalars().all()
        history = [{"role": m.role, "content": m.content} for m in reversed(history_objs)]
        
        # Retrieval
        retrieved_text = ""
        if active_course:
            vs = VectorStore(active_course.id, active_course.name, user.id)
            chunks = await vs.search(text, k=3)
            retrieved_text = "\n---\n".join([c["text"] for c in chunks])
            
        # Get Mode & Style from Preferences (mock for now)
        mode = user.preferences.get("mode", "QA")
        style = user.preferences.get("explanation_style", "simple")
        
        # LLM Call
        response = await tutor.get_response(
            user_id=user_id,
            message=text,
            history=history,
            context=retrieved_text,
            mode=mode,
            style=style
        )
        
        # Save to History
        user_msg = ConversationMessage(user_id=user.id, role="user", content=text)
        bot_msg = ConversationMessage(user_id=user.id, role="assistant", content=response)
        session.add(user_msg)
        session.add(bot_msg)
        await session.commit()
        
        await update.message.reply_text(response, parse_mode="Markdown")
