from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import Config

class Menus:
    @staticmethod
    def main_menu():
        keyboard = [
            [InlineKeyboardButton("📚 انتخاب درس", callback_data='menu_courses')],
            [InlineKeyboardButton("📝 کوییز جدید", callback_data='menu_quiz')],
            [InlineKeyboardButton("🗂 فلش‌کارت‌ها", callback_data='menu_flashcards')],
            [InlineKeyboardButton("📈 پیشرفت من", callback_data='menu_progress')],
            [InlineKeyboardButton("❓ راهنما", callback_data='menu_help')]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def course_selection():
        keyboard = []
        courses = Config.COURSES
        # Two in each row
        items = list(courses.items())
        for i in range(0, len(items), 2):
            row = []
            row.append(InlineKeyboardButton(items[i][1], callback_data=f"set_course_{items[i][0]}"))
            if i + 1 < len(items):
                row.append(InlineKeyboardButton(items[i+1][1], callback_data=f"set_course_{items[i+1][0]}"))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='menu_main')])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def quiz_difficulty():
        keyboard = [
            [
                InlineKeyboardButton("🟢 آسان", callback_data='quiz_diff_easy'),
                InlineKeyboardButton("🟡 متوسط", callback_data='quiz_diff_medium'),
                InlineKeyboardButton("🔴 سخت", callback_data='quiz_diff_hard')
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='menu_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
