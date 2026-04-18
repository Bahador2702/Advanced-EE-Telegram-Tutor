from typing import List, Dict, Optional
from collections import deque
from datetime import datetime
import json
import os

from utils.config import config


class ShortTermMemory:
    """Short-term conversation memory per user"""
    
    def __init__(self):
        self.memories: Dict[int, deque] = {}
        self.summaries: Dict[int, str] = {}
    
    def add_message(
        self,
        user_id: int,
        role: str,
        content: str,
        course_name: Optional[str] = None,
    ):
        if user_id not in self.memories:
            self.memories[user_id] = deque(maxlen=config.MAX_CONVERSATION_HISTORY)
        
        message = {
            "role": role,
            "content": content,
            "course": course_name,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.memories[user_id].append(message)
    
    def get_history(
        self,
        user_id: int,
        last_n: Optional[int] = None,
        course_name: Optional[str] = None,
    ) -> List[Dict]:
        if user_id not in self.memories:
            return []
        
        history = list(self.memories[user_id])
        
        if course_name:
            history = [m for m in history if m.get("course") == course_name]
        
        if last_n:
            history = history[-last_n:]
        
        return history
    
    def get_as_messages(self, user_id: int) -> List[Dict]:
        history = self.get_history(user_id)
        return [{"role": m["role"], "content": m["content"]} for m in history]
    
    def clear(self, user_id: int, course_name: Optional[str] = None):
        if user_id not in self.memories:
            return
        
        if course_name:
            self.memories[user_id] = deque(
                [m for m in self.memories[user_id] if m.get("course") != course_name],
                maxlen=config.MAX_CONVERSATION_HISTORY,
            )
        else:
            self.memories[user_id] = deque(maxlen=config.MAX_CONVERSATION_HISTORY)
            if user_id in self.summaries:
                del self.summaries[user_id]
    
    def get_summary(self, user_id: int) -> Optional[str]:
        return self.summaries.get(user_id)
    
    def save_to_disk(self, user_id: int, filepath: str):
        if user_id not in self.memories:
            return
        
        data = {
            "history": list(self.memories[user_id]),
            "summary": self.summaries.get(user_id),
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_disk(self, user_id: int, filepath: str):
        if not os.path.exists(filepath):
            return
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.memories[user_id] = deque(
            data.get("history", []),
            maxlen=config.MAX_CONVERSATION_HISTORY,
        )
        
        if data.get("summary"):
            self.summaries[user_id] = data["summary"]