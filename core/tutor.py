import logging
from openai import AsyncOpenAI
from core.prompts import Prompts
from utils.config import config
from typing import List, Dict

logger = logging.getLogger(__name__)

class Tutor:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )

    async def get_response(self, 
                             user_id: int, 
                             message: str, 
                             history: List[Dict[str, str]] = None,
                             context: str = "",
                             mode: str = "QA",
                             style: str = "simple") -> str:
        
        system_prompt = Prompts.construct_system_prompt(mode, style, context)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            # Only keep last N messages
            messages.extend(history[-config.MAX_CONVERSATION_HISTORY:])
            
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in LLM response: {e}")
            return "متأسفانه مشکلی در برقراری ارتباط با مغز متفکر من پیش آمده است. لطفاً کمی بعد دوباره امتحان کنید."

    async def generate_quiz(self, content: str) -> List[Dict]:
        messages = [
            {"role": "system", "content": Prompts.GENERATE_QUIZ},
            {"role": "user", "content": f"محتوای هدف:\n{content}"}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                response_format={"type": "json_object"}
            )
            import json
            data = json.loads(response.choices[0].message.content)
            return data.get("questions", [])
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return []
