from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from src.config import Config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    current_course = Column(String, default="general")
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Stats
    questions_count = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)

class Flashcard(Base):
    __tablename__ = 'flashcards'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course = Column(String)
    front = Column(Text)
    back = Column(Text)
    last_reviewed = Column(DateTime)
    next_review = Column(DateTime, default=datetime.datetime.utcnow)
    box = Column(Integer, default=1) # Leitner box level

class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course = Column(String)
    topic = Column(String)
    score = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    hard_questions = Column(JSON) # List of missed questions

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def get_or_create_user(self, telegram_id):
        session = self.get_session()
        user = session.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            user = User(telegram_id=str(telegram_id))
            session.add(user)
            session.commit()
            session.refresh(user)
        session.close()
        return user

    def update_user_course(self, telegram_id, course_slug):
        session = self.get_session()
        user = session.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if user:
            user.current_course = course_slug
            session.commit()
        session.close()
