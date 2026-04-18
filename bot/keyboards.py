from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
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


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Alias for get_main_keyboard (for compatibility)"""
    return get_main_keyboard()


def get_course_keyboard(courses: list) -> InlineKeyboardMarkup:
    """Keyboard for course selection"""
    keyboard = []
    for course in courses:
        keyboard.append([InlineKeyboardButton(course, callback_data=f"course_{course}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_mode_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for mode selection"""
    keyboard = [
        [
            InlineKeyboardButton("❓ QA", callback_data="mode_qa"),
            InlineKeyboardButton("🧮 Solver", callback_data="mode_solver"),
            InlineKeyboardButton("💡 Hint", callback_data="mode_hint"),
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_quiz_keyboard(question_index: int, total: int) -> InlineKeyboardMarkup:
    """Keyboard for quiz navigation"""
    keyboard = []
    
    # Option buttons (will be filled dynamically)
    for i in range(4):
        keyboard.append([InlineKeyboardButton(f"گزینه {i+1}", callback_data=f"quiz_opt_{i}")])
    
    # Navigation
    nav_buttons = []
    if question_index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ قبلی", callback_data="quiz_prev"))
    if question_index < total - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ بعدی", callback_data="quiz_next"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("❌ لغو کوییز", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)


def get_flashcard_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for flashcard review"""
    keyboard = [
        [InlineKeyboardButton("نمایش جواب", callback_data="flashcard_show_answer")],
        [
            InlineKeyboardButton("✅ آسان", callback_data="flashcard_easy"),
            InlineKeyboardButton("🤔 متوسط", callback_data="flashcard_medium"),
            InlineKeyboardButton("❌ سخت", callback_data="flashcard_hard"),
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back button keyboard"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)