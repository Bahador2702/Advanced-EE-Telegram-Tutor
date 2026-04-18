import re
from typing import Optional


class ModeDetector:
    """Automatically detect the required mode from user query"""
    
    async def detect(self, query: str) -> str:
        """
        Detect mode: 'solver', 'hint', or 'qa'
        """
        query_lower = query.lower()
        
        # Solver keywords (math, calculation, solve)
        solver_patterns = [
            r'\d+\s*[+\-*/^]',  # contains math operators
            r'محاسبه',
            r'حل کن',
            r'حل مسئله',
            r'calculate',
            r'solve',
            r'equal',
            r'معادله',
            r'\^',
            r'√',
            r'تابع',
            r'مشتق',
            r'انتگرال',
            r'حد',
            r'مجذور',
        ]
        
        for pattern in solver_patterns:
            if re.search(pattern, query_lower):
                return "solver"
        
        # Hint keywords
        hint_patterns = [
            r'راهنمایی',
            r'هینت',
            r'نکته',
            r'کمک',
            r'hint',
            r'help me',
            r'چگونه',
            r'روش حل',
        ]
        
        for pattern in hint_patterns:
            if re.search(pattern, query_lower):
                return "hint"
        
        # Default to QA
        return "qa"