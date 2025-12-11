import datetime
import enum
import os
from typing import List, Optional

import requests
from pydantic import BaseModel
from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy import create_engine,Column,Integer,String,Index,func,Enum,DateTime
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, Depends
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

database_url = "sqlite:///taskmind.db"
engine = create_engine(database_url,connect_args={"check_same_thread":False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

class PriorityEnum(enum.Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True,autoincrement=True)
    original_text = Column(String,nullable=False)
    title = Column(String,nullable=False)
    priority = Column(Enum(PriorityEnum),default=PriorityEnum.Medium)
    deadline = Column(String,nullable=False)
    category = Column(String,nullable=False)
    notes = Column(String,nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())


Base.metadata.create_all(engine)

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
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_API_URL = "https://api.groq.ai/v1/llm"
    prompt = f"""
        Your are an AI task organizer, Take this task description and return a JSON with:
        title,priority(High,Medium,Low),category,deadline,notes.
        Task: {task_text}
        """
    payload = {
        "prompt": prompt,
        "max_tokens":100
    }

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            results = response.json()
            return results.get("text")
        except:
            return {}
    return {}


@app.post("/task",response_model=ReadTask)
def create_task(task: CreateTask,db: Session = Depends(get_db)):
    refined_task = reform_with_llm(task.original_text)
    db_task = Task(
        original_text = task.original_text,
        title = refined_task.get("title"),
        priority = refined_task.get("priority"),
        deadline = refined_task.get("deadline"),
        category = refined_task.get("category"),
        notes = refined_task.get("notes"),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks",response_model=List[ReadTask])
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks









