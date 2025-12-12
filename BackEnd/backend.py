import datetime
import enum
import json
import os
from typing import List, Optional
import requests
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Index, func, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI()

database_url = "sqlite:///data/taskmind.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class PriorityEnum(enum.Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_text = Column(String, nullable=False)
    title = Column(String, nullable=True, default="Untitled Task")
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.Medium)
    deadline = Column(String, nullable=True, default="No deadline")
    category = Column(String, nullable=True, default="General")
    notes = Column(String, nullable=True, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


Base.metadata.create_all(engine)


class TaskDetails(BaseModel):
    title: str = Field(description="The title of the task.")
    priority: str = Field(description="Priority level:  High, Medium, or Low.")
    category: str = Field(description="Category of the task.")
    deadline: str = Field(description="Deadline for the task.")
    notes: str = Field(description="Additional notes for the task.")


class CreateTask(BaseModel):
    original_text: str


class ReadTask(BaseModel):
    id: int
    original_text: str
    title: str
    priority: PriorityEnum
    deadline: Optional[str]
    category: Optional[str]
    notes: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reform_with_llm(task_text: str) -> dict:
    """Use Groq API for fast AI task parsing"""

    api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key:
        print("No GROQ_API_KEY found - using basic parsing")
        return fallback_parsing(task_text)

    try:
        print(f"Analyzing task with Groq:  {task_text}")

        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a task organizer.  Analyze tasks and return JSON with keys: title, priority (High/Medium/Low), category, deadline, notes."
                },
                {
                    "role": "user",
                    "content": f"Analyze this task and return ONLY valid JSON:\n\nTask: {task_text}\n\nJSON:"
                }
            ],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        content = completion.choices[0].message.content
        print(f"Groq response: {content}")

        parsed_data = json.loads(content)

        # Validate priority
        if parsed_data.get("priority") not in ["High", "Medium", "Low"]:
            parsed_data["priority"] = "Medium"

        # Ensure all fields exist
        parsed_data.setdefault("title", task_text[: 50])
        parsed_data.setdefault("category", "General")
        parsed_data.setdefault("deadline", "No deadline")
        parsed_data.setdefault("notes", "")

        return parsed_data

    except Exception as e:
        print(f"Groq error: {e}")
        return fallback_parsing(task_text)


def fallback_parsing(task_text: str) -> dict:
    """Simple keyword-based parsing as fallback"""

    text_lower = task_text.lower()

    # Detect priority
    high_keywords = ['urgent', 'important', 'critical', 'asap', 'emergency', 'crucial']
    low_keywords = ['later', 'someday', 'maybe', 'eventually']

    if any(word in text_lower for word in high_keywords):
        priority = 'High'
    elif any(word in text_lower for word in low_keywords):
        priority = 'Low'
    else:
        priority = 'Medium'

    # Detect category
    if any(word in text_lower for word in ['buy', 'shop', 'groceries', 'store']):
        category = 'Shopping'
    elif any(word in text_lower for word in ['meeting', 'work', 'project', 'deadline', 'report']):
        category = 'Work'
    elif any(word in text_lower for word in ['gym', 'doctor', 'appointment', 'exercise']):
        category = 'Personal'
    else:
        category = 'General'

    # Detect deadline
    deadline = "No deadline"
    if 'today' in text_lower:
        deadline = 'Today'
    elif 'tomorrow' in text_lower:
        deadline = 'Tomorrow'
    elif any(day in text_lower for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
        deadline = 'This week'

    return {
        "title": task_text[:50] if len(task_text) <= 50 else task_text[: 47] + "...",
        "priority": priority,
        "category": category,
        "deadline": deadline,
        "notes": ""
    }


@app.post("/task", response_model=ReadTask)
def create_task(task: CreateTask, db: Session = Depends(get_db)):
    refined_task = reform_with_llm(task.original_text)

    # Map priority string to PriorityEnum
    priority_str = refined_task.get("priority", "Medium")
    try:
        priority_enum = PriorityEnum[priority_str]
    except (KeyError, TypeError):
        priority_enum = PriorityEnum.Medium

    db_task = Task(
        original_text=task.original_text,
        title=refined_task.get("title", "Untitled Task"),
        priority=priority_enum,
        deadline=refined_task.get("deadline", "No deadline"),
        category=refined_task.get("category", "General"),
        notes=refined_task.get("notes", ""),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=List[ReadTask])
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks