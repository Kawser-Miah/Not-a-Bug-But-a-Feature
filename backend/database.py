from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL
DATABASE_URL = "sqlite:///./hackathon.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    time_duration = Column(Integer, nullable=False)  # minutes per day
    interests = Column(JSON, nullable=False)  # list of interests
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    task_failures = relationship("TaskFailure", back_populates="user", cascade="all, delete-orphan")

class Roadmap(Base):
    __tablename__ = "roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    steps = Column(JSON, nullable=False)  # list of roadmap steps
    current_step = Column(Integer, nullable=False, default=1)  # 1-based index into steps
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="roadmaps")
    tasks = relationship("Task", back_populates="roadmap", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    step_num = Column(Integer, nullable=True)  # which roadmap step this task belongs to
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    assigned_time = Column(DateTime, nullable=False)
    sources = Column(JSON, nullable=False, default=list)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    roadmap = relationship("Roadmap", back_populates="tasks")
    failures = relationship("TaskFailure", back_populates="task", cascade="all, delete-orphan")

class TaskFailure(Base):
    __tablename__ = "task_failures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    failure_reason = Column(Text, nullable=False)
    failure_date = Column(DateTime, default=datetime.utcnow)
    tasks_completed_count = Column(Integer, default=0)  # how many tasks were completed
    total_tasks_count = Column(Integer, default=0)  # total tasks assigned
    
    # Relationships
    user = relationship("User", back_populates="task_failures")
    task = relationship("Task", back_populates="failures")

# Create tables via Alembic migrations (do not call create_all here)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
