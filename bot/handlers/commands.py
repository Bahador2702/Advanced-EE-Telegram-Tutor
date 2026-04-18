import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db.database import AsyncSessionLocal, get_sync_session
from db import models
from bot.keyboards import get_main_keyboard

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = update.effective_user.id
    
    # Save user to database
    try:
        async with AsyncSessionLocal() as session:
            # Check if user exists
            from sqlalchemy import select
            stmt = select(models.User).where(models.User.telegram_id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                # Create new user
                new_user = models.User(
                    telegram_id=user_id,
                    username=user.username,
                    first_name=user.first_name,
                )
                session.add(new_user)
                await session.commit()
                logger.info(f"New user created: {user_id}")
    except Exception as e:
        logger.error(f"Database error in start_command: {e}")
    
    # Welcome message
    welcome_text = f"""
سلام {user.first_name}! 👋

به **استاد خصوصی هوش مصنوعی** خوش آمدی.

من یک معلم خصوصی هوشمند هستم که می‌تواند:
📚 به سوالات درسی پاسخ دهد
🧮 مسائل ریاضی را گام به گام حل کند
📝 از جزوه‌های تو یاد بگیرد
🎯 کوییز و فلش‌کارت بسازد

**برای شروع:**
1. یک درس جدید بساز: `/new_course [نام درس]`
2. جزوه آپلود کن: `/upload`
3. سوال بپرس!

از منوی زیر می‌توانی استفاده کنی:
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 **راهنمای دستورات**

**مدیریت دروس:**
• `/new_course [نام]` - ایجاد درس جدید
• `/courses` - لیست دروس
• `/course [نام]` - انتخاب درس فعال
• `/delete_course [نام]` - حذف درس

**مدیریت فایل‌ها:**
• `/upload` - آپلود جزوه (PDF, DOCX, TXT)
• `/files` - لیست فایل‌های درس فعال
• `/delete_file [نام]` - حذف فایل

**حالت‌های پاسخگویی:**
• `/mode qa` - حالت پرسش و پاسخ
• `/mode solver` - حالت حل مسئله
• `/mode hint` - حالت راهنمایی

**ابزارهای مطالعه:**
• `/quiz` - شروع کوییز
• `/flashcards` - مرور فلش‌کارت‌ها
• `/summarize` - خلاصه گرفتن از درس

**سایر:**
• `/stats` - آمار پیشرفت
• `/reset_session` - پاک کردن حافظه مکالمه
• `/help` - این راهنما
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def new_course_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /new_course command"""
    user_id = update.effective_user.id
    
    # Get course name from arguments
    if not context.args:
        await update.message.reply_text(
            "❌ لطفاً نام درس را وارد کن.\n\n"
            "مثال: `/new_course ریاضی ۱`",
            parse_mode="Markdown",
        )
        return
    
    course_name = " ".join(context.args)
    
    # Save to database
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            # Get user
            stmt = select(models.User).where(models.User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                await update.message.reply_text("❌ ابتدا /start را بزن.")
                return
            
            # Check if course already exists
            stmt = select(models.Course).where(
                models.Course.user_id == user.id,
                models.Course.name == course_name
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                await update.message.reply_text(f"❌ درس «{course_name}» قبلاً ایجاد شده است.")
                return
            
            # Create new course
            new_course = models.Course(
                user_id=user.id,
                name=course_name,
            )
            session.add(new_course)
            await session.commit()
            
            # Set as active course
            user.active_course = course_name
            await session.commit()
            
            await update.message.reply_text(
                f"✅ درس «{course_name}» با موفقیت ایجاد شد.\n\n"
                f"این درس هم‌اکنون فعال است.\n"
                f"حالا می‌توانی جزوه آپلود کنی: `/upload`",
                parse_mode="Markdown",
            )
            
    except Exception as e:
        logger.error(f"Error in new_course_command: {e}")
        await update.message.reply_text("❌ خطا در ایجاد درس. لطفاً دوباره تلاش کن.")


async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /courses command - list all courses"""
    user_id = update.effective_user.id
    
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            stmt = select(models.User).where(models.User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                await update.message.reply_text("❌ ابتدا /start را بزن.")
                return
            
            stmt = select(models.Course).where(models.Course.user_id == user.id)
            result = await session.execute(stmt)
            courses = result.scalars().all()
            
            if not courses:
                await update.message.reply_text(
                    "📚 **درسی وجود ندارد**\n\n"
                    "برای ایجاد درس جدید: `/new_course [نام درس]`",
                    parse_mode="Markdown",
                )
                return
            
            course_list = "\n".join([f"• {c.name}" + (" ✅" if user.active_course == c.name else "") for c in courses])
            
            await update.message.reply_text(
                f"📚 **دروس شما:**\n\n{course_list}\n\n"
                f"برای انتخاب درس فعال: `/course [نام درس]`",
                parse_mode="Markdown",
            )
            
    except Exception as e:
        logger.error(f"Error in courses_command: {e}")
        await update.message.reply_text("❌ خطا در دریافت لیست دروس.")


async def course_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /course command - switch active course"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ لطفاً نام درس را وارد کن.\n\n"
            "مثال: `/course ریاضی ۱`",
            parse_mode="Markdown",
        )
        return
    
    course_name = " ".join(context.args)
    
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            stmt = select(models.User).where(models.User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                await update.message.reply_text("❌ ابتدا /start را بزن.")
                return
            
            # Check if course exists
            stmt = select(models.Course).where(
                models.Course.user_id == user.id,
                models.Course.name == course_name
            )
            result = await session.execute(stmt)
            course = result.scalar_one_or_none()
            
            if not course:
                await update.message.reply_text(f"❌ درس «{course_name}» وجود ندارد.")
                return
            
            # Set active course
            user.active_course = course_name
            await session.commit()
            
            await update.message.reply_text(
                f"✅ درس «{course_name}» فعال شد.\n\n"
                f"حالا می‌توانی سوالاتت را از این درس بپرسی.",
                parse_mode="Markdown",
            )
            
    except Exception as e:
        logger.error(f"Error in course_command: {e}")
        await update.message.reply_text("❌ خطا در انتخاب درس.")


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command - change response mode"""
    if not context.args:
        await update.message.reply_text(
            "🎯 **تغییر حالت پاسخگویی**\n\n"
            "حالت‌های موجود:\n"
            "• `qa` - پرسش و پاسخ معمولی\n"
            "• `solver` - حل گام به گام مسائل\n"
            "• `hint` - فقط راهنمایی (بدون جواب مستقیم)\n\n"
            "مثال: `/mode solver`",
            parse_mode="Markdown",
        )
        return
    
    mode = context.args[0].lower()
    
    if mode not in ["qa", "solver", "hint"]:
        await update.message.reply_text("❌ حالت نامعتبر. حالت‌های مجاز: qa, solver, hint")
        return
    
    context.user_data["mode"] = mode
    
    mode_names = {"qa": "پرسش و پاسخ", "solver": "حل مسئله", "hint": "راهنمایی"}
    
    await update.message.reply_text(
        f"✅ حالت **{mode_names[mode]}** فعال شد.\n\n"
        f"حالا سوالاتت را بپرس.",
        parse_mode="Markdown",
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show progress stats"""
    user_id = update.effective_user.id
    
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            stmt = select(models.User).where(models.User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                await update.message.reply_text("❌ ابتدا /start را بزن.")
                return
            
            # Get quiz stats
            stmt = select(models.QuizResult).where(models.QuizResult.user_id == user.id)
            result = await session.execute(stmt)
            quizzes = result.scalars().all()
            
            total = len(quizzes)
            correct = sum(1 for q in quizzes if q.is_correct)
            
            if total > 0:
                stats_text = f"""
📊 **آمار پیشرفت تحصیلی**

• کوییزهای انجام شده: {total}
• پاسخ‌های صحیح: {correct}
• پاسخ‌های غلط: {total - correct}
• نرخ موفقیت: {int(correct/total*100)}%

درس فعال: {user.active_course or "ندارد"}
"""
            else:
                stats_text = f"""
📊 **آمار پیشرفت تحصیلی**

هنوز کوییز حل نکرده‌ای.
برای شروع: `/quiz`

درس فعال: {user.active_course or "ندارد"}
"""
            
            await update.message.reply_text(stats_text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await update.message.reply_text("❌ خطا در دریافت آمار.")