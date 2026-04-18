import os
import shutil
from sqlalchemy.future import select
from db.models import Course, User as DBUser
from utils.config import config
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class CourseManager:
    @staticmethod
    async def create_course(session: AsyncSession, telegram_id: int, name: str):
        # Find user
        q = select(DBUser).where(DBUser.telegram_id == telegram_id)
        res = await session.execute(q)
        user = res.scalar_one_or_none()
        
        if not user:
            return None, "User not found."

        # Check if course exists for this user
        q = select(Course).where(Course.user_id == user.id, Course.name == name)
        res = await session.execute(q)
        if res.scalar_one_or_none():
            return None, "نام درس تکراری است."

        new_course = Course(user_id=user.id, name=name)
        session.add(new_course)
        await session.commit()
        
        # Create directory
        course_path = os.path.join(config.COURSES_DIR, str(user.id), name)
        os.makedirs(course_path, exist_ok=True)
        
        return new_course, None

    @staticmethod
    async def get_user_courses(session: AsyncSession, telegram_id: int):
        q = select(Course).join(DBUser).where(DBUser.telegram_id == telegram_id)
        res = await session.execute(q)
        return res.scalars().all()

    @staticmethod
    async def delete_course(session: AsyncSession, telegram_id: int, name: str):
        q = select(Course).join(DBUser).where(DBUser.telegram_id == telegram_id, Course.name == name)
        res = await session.execute(q)
        course = res.scalar_one_or_none()
        
        if not course:
            return False, "درس پیدا نشد."

        # Delete database record
        await session.delete(course)
        await session.commit()
        
        # Delete files
        course_path = os.path.join(config.COURSES_DIR, str(course.user_id), name)
        if os.path.exists(course_path):
            shutil.rmtree(course_path)
            
        return True, "درس با موفقیت حذف شد."
