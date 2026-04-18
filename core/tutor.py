import logging
from typing import List, Dict, Optional, AsyncGenerator
from openai import AsyncOpenAI

from utils.config import config
from core.prompts import (
    get_qa_prompt,
    get_solver_prompt,
    get_hint_prompt,
    get_evaluation_prompt,
    get_socratic_question_prompt,
)
from core.mode_detector import ModeDetector

logger = logging.getLogger(__name__)


class Tutor:
    """Core LLM tutor class"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
        )
        self.mode_detector = ModeDetector()
        self.conversation_history: Dict[int, List[Dict]] = {}
        
    async def respond(
        self,
        user_id: int,
        user_message: str,
        context: str = "",
        mode: Optional[str] = None,
        course_name: Optional[str] = None,
    ) -> str:
        """Generate response based on mode and context"""
        
        # Auto-detect mode if not specified
        if mode is None:
            mode = await self.mode_detector.detect(user_message)
        
        logger.info(f"User {user_id} | Mode: {mode} | Course: {course_name}")
        
        # Get appropriate prompt template
        if mode == "solver":
            system_prompt = get_solver_prompt(context, user_message)
        elif mode == "hint":
            system_prompt = get_hint_prompt(context, user_message)
        else:  # qa mode (default)
            system_prompt = get_qa_prompt(context, course_name)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history (last N messages)
        history = self.conversation_history.get(user_id, [])[-config.MAX_CONVERSATION_HISTORY:]
        messages.extend(history)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
            )
            
            answer = response.choices[0].message.content
            
            # Update history
            self._update_history(user_id, user_message, answer)
            
            return answer
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "⚠️ متأسفانه در ارتباط با سرور هوش مصنوعی خطایی رخ داد. لطفاً چند لحظه دیگر دوباره تلاش کن."
    
    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        context: str = "",
    ) -> Dict:
        """Evaluate student's answer"""
        
        prompt = get_evaluation_prompt(question, user_answer, correct_answer, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return {
                "is_correct": result.get("is_correct", False),
                "score": result.get("score", 0),
                "feedback": result.get("feedback", ""),
                "explanation": result.get("explanation", ""),
            }
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return {
                "is_correct": False,
                "score": 0,
                "feedback": "خطا در ارزیابی پاسخ.",
                "explanation": "",
            }
    
    async def generate_socratic_question(
        self,
        topic: str,
        student_previous_answer: Optional[str] = None,
        context: str = "",
    ) -> str:
        """Generate a Socratic guiding question"""
        
        prompt = get_socratic_question_prompt(topic, student_previous_answer, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Socratic question error: {e}")
            return f"به نظرت درباره {topic} چه می‌دانی؟"
    
    def _update_history(self, user_id: int, user_msg: str, assistant_msg: str):
        """Update conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({"role": "user", "content": user_msg})
        self.conversation_history[user_id].append({"role": "assistant", "content": assistant_msg})
        
        # Trim if too long
        if len(self.conversation_history[user_id]) > config.MAX_CONVERSATION_HISTORY * 2:
            self.conversation_history[user_id] = self.conversation_history[user_id][-config.MAX_CONVERSATION_HISTORY * 2:]
    
    def clear_history(self, user_id: int):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
            logger.info(f"Cleared history for user {user_id}")