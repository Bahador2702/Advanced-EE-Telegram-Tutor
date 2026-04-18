from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ContextTypes
from db.database import async_session
from db.models import User, Course
from sqlalchemy.future import select
from courses.course_manager import CourseManager
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with async_session() as session:
        # Get or Create User
        q = select(User).where(User.telegram_id == update.effective_user.id)
        res = await session.execute(q)
        user = res.scalar_one_or_none()
        
        if not user:
            user = User(
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name
            )
            session.add(user)
            await session.commit()
            
    welcome_text = (
        "سلام دانشجوی عزیز! 👋\n"
        "من دستیار هوشمند شما در مهندسی برق هستم.\n\n"
        "شما می‌توانید درس‌های خود را بسازید، جزوه آپلود کنید و با من تمرین کنید.\n"
        "برای شروع، یک درس جدید بسازید:\n"
        "/new_course <نام درس>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 لیست درس‌ها", callback_data="list_courses")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def new_course_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("لطفاً نام درس را بنویسید:\nمثال: `/new_course مدارهای_الکتریکی`", parse_mode="Markdown")
        return
        
    course_name = "_".join(context.args)
    async with async_session() as session:
        course, error = await CourseManager.create_course(session, update.effective_user.id, course_name)
        
        if error:
            await update.message.reply_text(f"❌ خطا: {error}")
        else:
            await update.message.reply_text(f"✅ درس '{course_name}' با موفقیت ساخته شد.")

async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with async_session() as session:
        courses = await CourseManager.get_user_courses(session, update.effective_user.id)
        
        if not courses:
            await update.message.reply_text("شما هنوز درسی نساخته‌اید.")
            return
            
        text = "📚 لیست درس‌های شما:\n\n"
        keyboard = []
        for c in courses:
            text += f"• {c.name}\n"
            keyboard.append([InlineKeyboardButton(c.name, callback_data=f"select_course_{c.id}")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 **راهنمای دستورات:**\n\n"
        "/new_course <name> - ساخت درس جدید\n"
        "/courses - لیست درس‌ها و انتخاب\n"
        "/files - مدیریت فایل‌های درس فعلی\n"
        "/quiz - شروع کوییز\n"
        "/mode - تغییر حالت پاسخگویی\n"
        "/stats - آمار پیشرفت\n"
        "/reset_session - پاک کردن حافظه موقت"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Placeholder commands for structure
async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def course_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def delete_course_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def files_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def delete_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def hint_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def flashcards_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def study_plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def reset_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def debug_retrieval_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def retry_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE): pass
