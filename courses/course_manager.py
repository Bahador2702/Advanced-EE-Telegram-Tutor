# اضافه کن به class CourseManager:

def get_active_course(self, user_id: int) -> str:
    """Get active course for user"""
    # Try from memory first
    if user_id in self.active_courses:
        return self.active_courses[user_id]
    
    # Try from database
    session = self.db_session()
    try:
        from db.models import User
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if user and user.active_course:
            self.active_courses[user_id] = user.active_course
            return user.active_course
    finally:
        session.close()
    
    return None

def set_active_course(self, user_id: int, course_name: str) -> bool:
    """Set active course for user"""
    # Validate course exists
    if course_name not in self.get_user_courses(user_id):
        return False
    
    self.active_courses[user_id] = course_name
    
    # Save to database
    session = self.db_session()
    try:
        from db.models import User
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if user:
            user.active_course = course_name
            session.commit()
    finally:
        session.close()
    
    return True