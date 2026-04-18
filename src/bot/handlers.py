import os
import json
from telegram import Update, constants
from telegram.ext import ContextTypes
from src.config import Config
from src.llm.client import LLMClient
from src.tutor.prompts import Prompts
from src.database.manager import DatabaseManager
from src.retrieval.rag import RAGManager
from src.bot.menus import Menus

class BotHandlers:
    def __init__(self):
        self.llm = LLMClient()
        self.db = DatabaseManager()
        self.rag = RAGManager()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.db.get_or_create_user(update.effective_user.id)
        welcome_text = (
            f"سلام {update.effective_user.first_name} عزیز! 👋\n"
            "به دستیار هوشمند مهندسی برق خوش آمدی.\n\n"
            "من می‌توانم در دروس مختلف برق به تو کمک کنم، مسائل را حل کنم و حتی از جزواتت کوییز بسازم."
        )
        await update.message.reply_text(welcome_text, reply_markup=Menus.main_menu())

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == 'menu_courses':
            await query.edit_message_text("لطفاً درس مورد نظر خود را انتخاب کنید:", reply_markup=Menus.course_selection())
        
        elif data.startswith("set_course_"):
            course_slug = data.replace("set_course_", "")
            self.db.update_user_course(update.effective_user.id, course_slug)
            course_name = Config.COURSES.get(course_slug)
            await query.edit_message_text(f"✅ درس فعال تغییر یافت به: {course_name}", reply_markup=Menus.main_menu())

        elif data == 'menu_main':
            await query.edit_message_text("منوی اصلی:", reply_markup=Menus.main_menu())

        elif data == 'menu_progress':
            user = self.db.get_or_create_user(update.effective_user.id)
            course_name = Config.COURSES.get(user.current_course, "عمومی")
            progress_text = (
                "📊 **گزارش پیشرفت شما**\n\n"
                f"📚 درس فعلی: {course_name}\n"
                f"❓ سوالات پرسیده شده: {user.questions_count}\n"
                f"✅ پاسخ‌های صحیح در کوییز: {user.correct_answers}\n"
            )
            await query.edit_message_text(progress_text, parse_mode=constants.ParseMode.MARKDOWN, reply_markup=Menus.main_menu())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        user = self.db.get_or_create_user(update.effective_user.id)
        
        # Simple Mode Detection
        mode = "QA"
        if any(w in text.lower() for w in ["حل کن", "محاسبه", "جواب", "=", "+", "انتگرال"]):
            mode = "SOLVER"
        elif any(w in text.lower() for w in ["مدار", "خازن", "مقاومت", "فیلتر", "گره"]):
            mode = "CIRCUIT"

        # RAG Context
        retrieved_context = self.rag.retrieve(text, user.current_course)
        
        system_prompt = Prompts.get_prompt_for_mode(mode, retrieved_context)
        
        await update.message.reply_chat_action(constants.ChatAction.TYPING)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        response = self.llm.chat_completion(messages)
        answer = response.choices[0].message.content
        
        await update.message.reply_text(answer, parse_mode=constants.ParseMode.MARKDOWN)

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        doc = update.message.document
        user = self.db.get_or_create_user(update.effective_user.id)
        
        await update.message.reply_text("⏱ در حال دریافت و ایندکس کردن فایل شما...")
        
        file = await context.bot.get_file(doc.file_id)
        file_path = os.path.join(Config.UPLOADS_DIR, doc.file_name)
        await file.download_to_drive(file_path)
        
        # Index in RAG
        self.rag.index_file(file_path, user.current_course)
        
        await update.message.reply_text(f"✅ فایل '{doc.file_name}' با موفقیت به منابع درس '{Config.COURSES.get(user.current_course)}' اضافه شد.")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1] # Largest size
        file = await context.bot.get_file(photo.file_id)
        
        # Download bytes
        photo_bytes = await file.download_as_bytearray()
        
        await update.message.reply_chat_action(constants.ChatAction.TYPING)
        
        caption = update.message.caption or "این تصویر مدار یا مسئله مهندسی برق است. لطفاً آن را تحلیل کن."
        prompt = f"{Prompts.BASE_SYSTEM}\n{caption}"
        
        response = self.llm.analyze_image(prompt, bytes(photo_bytes))
        answer = response.choices[0].message.content
        
        await update.message.reply_text(answer, parse_mode=constants.ParseMode.MARKDOWN)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        path = os.path.join(Config.UPLOADS_DIR, f"voice_{update.effective_user.id}.ogg")
        await file.download_to_drive(path)
        
        transcript = self.llm.transcribe_audio(path)
        if transcript:
            # Re-route to text handler
            update.message.text = transcript
            await self.handle_message(update, context)
        else:
            await update.message.reply_text("❌ متأسفانه متوجه صدای شما نشدم.")
