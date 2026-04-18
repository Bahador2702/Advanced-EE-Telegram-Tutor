import json
import os
from typing import List, Dict, Optional
from pathlib import Path

from utils.config import config


class CourseManager:
    """Manage user courses - create, delete, switch, list"""
    
    def __init__(self):
        self.courses_dir = Path(config.COURSES_DIR)
        self.courses_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for active courses
        self.active_courses: Dict[int, str] = {}
        
        # Database session (will be set from main.py)
        self.db_session = None
    
    def set_db_session(self, session):
        """Set database session for persistence"""
        self.db_session = session
    
    def create_course(self, user_id: int, course_name: str) -> bool:
        """Create a new course for user"""
        # Sanitize course name
        course_name = course_name.strip().replace(" ", "_")
        
        # Get user's courses
        courses = self.get_user_courses(user_id)
        
        if course_name in courses:
            return False
        
        # Create course directory
        course_dir = self.courses_dir / str(user_id) / course_name
        course_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file
        metadata = {
            "name": course_name,
            "user_id": user_id,
            "created_at": str(Path(course_dir).stat().st_ctime),
            "files": [],
            "total_chunks": 0,
        }
        
        with open(course_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Save to database if available
        if self.db_session:
            try:
                from db.models import Course
                course = Course(
                    user_id=user_id,
                    name=course_name,
                )
                self.db_session.add(course)
                self.db_session.commit()
            except Exception as e:
                print(f"Database error: {e}")
        
        return True
    
    def get_user_courses(self, user_id: int) -> List[str]:
        """Get list of all courses for a user"""
        user_dir = self.courses_dir / str(user_id)
        
        if not user_dir.exists():
            return []
        
        courses = []
        for item in user_dir.iterdir():
            if item.is_dir() and (item / "metadata.json").exists():
                courses.append(item.name)
        
        return courses
    
    def get_active_course(self, user_id: int) -> Optional[str]:
        """Get active course for user"""
        # Check memory cache first
        if user_id in self.active_courses:
            return self.active_courses[user_id]
        
        # Try from database
        if self.db_session:
            try:
                from db.models import User
                user = self.db_session.query(User).filter(User.telegram_id == user_id).first()
                if user and user.active_course:
                    self.active_courses[user_id] = user.active_course
                    return user.active_course
            except Exception as e:
                print(f"Database error: {e}")
        
        return None
    
    def set_active_course(self, user_id: int, course_name: str) -> bool:
        """Set active course for user"""
        # Validate course exists
        if course_name not in self.get_user_courses(user_id):
            return False
        
        # Update memory cache
        self.active_courses[user_id] = course_name
        
        # Save to database if available
        if self.db_session:
            try:
                from db.models import User
                user = self.db_session.query(User).filter(User.telegram_id == user_id).first()
                if user:
                    user.active_course = course_name
                    self.db_session.commit()
            except Exception as e:
                print(f"Database error: {e}")
        
        return True
    
    def delete_course(self, user_id: int, course_name: str) -> bool:
        """Delete a course"""
        course_dir = self.courses_dir / str(user_id) / course_name
        
        if not course_dir.exists():
            return False
        
        # Delete directory and all contents
        import shutil
        shutil.rmtree(course_dir)
        
        # Remove from database if available
        if self.db_session:
            try:
                from db.models import Course
                course = self.db_session.query(Course).filter(
                    Course.user_id == user_id,
                    Course.name == course_name
                ).first()
                if course:
                    self.db_session.delete(course)
                    self.db_session.commit()
            except Exception as e:
                print(f"Database error: {e}")
        
        # Clear active course if it was this one
        if self.active_courses.get(user_id) == course_name:
            del self.active_courses[user_id]
        
        return True
    
    def get_course_path(self, user_id: int, course_name: str) -> Path:
        """Get filesystem path for a course"""
        return self.courses_dir / str(user_id) / course_name
    
    def course_exists(self, user_id: int, course_name: str) -> bool:
        """Check if course exists"""
        return course_name in self.get_user_courses(user_id)