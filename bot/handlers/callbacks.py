import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from courses.course_manager import CourseManager
from core.tutor import Tutor
from utils.config import config

logger = logging.getLogger(__name__)

# Global instances
course_manager: CourseManager = None
tutor: Tutor = None


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all inline keyboard callbacks"""
    
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    # Course selection
    if data.startswith("course_"):
        course_name = data.replace("course_", "")
        course_manager.set_active_course(user_id, course_name)
        await query.edit_message_text(
            f"✅ درس **{course_name}** فعال شد.\n\n"
            f"حالا می‌توانی سوالاتت را از این درس بپرسی یا جزوه جدید آپلود کنی.",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "list_courses":
        courses = course_manager.get_user_courses(user_id)
        if not courses:
            await query.edit_message_text(
                "📚 **درسی وجود ندارد**\n\n"
                "برای ایجاد درس جدید از دستور `/new_course` استفاده کن.",
                parse_mode="Markdown",
            )
            return
        
        keyboard = []
        for course in courses:
            keyboard.append([InlineKeyboardButton(course, callback_data=f"course_{course}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
        
        await query.edit_message_text(
            "📚 **انتخاب درس فعال**:\n\nروی هر درس بزن تا فعال شود:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    
    # Mode selection
    elif data == "mode_qa":
        context.user_data["mode"] = "qa"
        await query.edit_message_text(
            "✅ حالت **پرسش و پاسخ** فعال شد.\n\n"
            "می‌توانی هر سوال درسی بپرسی و من بر اساس جزوه‌ات پاسخ می‌دهم.",
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "mode_solver":
        context.user_data["mode"] = "solver"
        await query.edit_message_text(
            "✅ حالت **حل مسئله** فعال شد.\n\n"
            "سوال ریاضی یا محاسباتی خود را بفرست. راه‌حل را گام به گام توضیح می‌دهم.",
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "mode_hint":
        context.user_data["mode"] = "hint"
        await query.edit_message_text(
            "✅ حالت **راهنمایی تدریجی** فعال شد.\n\n"
            "من جواب مستقیم نمی‌دهم، بلکه با راهنمایی تو را به پاسخ می‌رسانم.",
            reply_markup=get_main_menu_keyboard(),
        )
    
    # Navigation
    elif data == "back_to_main":
        await query.edit_message_text(
            "🔰 **منوی اصلی**\n\nیکی از گزینه‌های زیر را انتخاب کن:",
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "help":
        await query.edit_message_text(
            "📖 **راهنمای سریع**\n\n"
            "• `/new_course [نام]` - ایجاد درس جدید\n"
            "• `/upload` - آپلود جزوه (PDF، DOCX، TXT)\n"
            "• `/quiz` - شروع کوییز\n"
            "• `/flashcards` - مرور فلش‌کارت‌ها\n"
            "• `/summarize` - خلاصه گرفتن از درس\n"
            "• `/mode` - تغییر حالت پاسخگویی\n"
            "• `/stats` - مشاهده پیشرفت\n\n"
            "برای دیدن همه دستورات: `/help`",
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "stats":
        active_course = course_manager.get_active_course(user_id)
        if not active_course:
            await query.edit_message_text(
                "❌ ابتدا یک درس فعال انتخاب کن.",
                reply_markup=get_main_menu_keyboard(),
            )
            return
        
        await query.edit_message_text(
            f"📊 **آمار پیشرفت - {active_course}**\n\n"
            f"این بخش در حال تکمیل است.\n"
            f"به زودی آمار دقیق‌تری خواهی دید.",
            reply_markup=get_main_menu_keyboard(),
        )
    
    # Quiz and Flashcards (placeholders)
    elif data == "quiz_start":
        active_course = course_manager.get_active_course(user_id)
        if not active_course:
            await query.edit_message_text(
                "❌ ابتدا یک درس فعال انتخاب کن.",
                reply_markup=get_main_menu_keyboard(),
            )
            return
        
        await query.edit_message_text(
            f"📝 **کوییز - {active_course}**\n\n"
            f"این بخش در حال تکمیل است.\n"
            f"به زودی می‌توانی کوییز بدهی.",
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "flashcards_review":
        active_course = course_manager.get_active_course(user_id)
        if not active_course:
            await query.edit_message_text(
                "❌ ابتدا یک درس فعال انتخاب کن.",
                reply_markup=get_main_menu_keyboard(),
            )
            return
        
        await query.edit_message_text(
            f"📇 **فلش‌کارت - {active_course}**\n\n"
            f"این بخش در حال تکمیل است.\n"
            f"به زودی می‌توانی فلش‌کارت مرور کنی.",
            reply_markup=get_main_menu_keyboard(),
        )


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build main menu inline keyboard"""
    
    keyboard = [
        [InlineKeyboardButton("📚 انتخاب درس", callback_data="list_courses")],
        [
            InlineKeyboardButton("❓ QA", callback_data="mode_qa"),
            InlineKeyboardButton("🧮 Solver", callback_data="mode_solver"),
            InlineKeyboardButton("💡 Hint", callback_data="mode_hint"),
        ],
        [
            InlineKeyboardButton("📝 کوییز", callback_data="quiz_start"),
            InlineKeyboardButton("📇 فلش‌کارت", callback_data="flashcards_review"),
        ],
        [
            InlineKeyboardButton("📊 آمار", callback_data="stats"),
            InlineKeyboardButton("📖 راهنما", callback_data="help"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)


def set_instances(cm: CourseManager, t: Tutor):
    """Set global instances from main.py"""
    global course_manager, tutor
    course_manager = cm
    tutor = t