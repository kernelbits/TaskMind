import datetime
import enum
import json
from typing import List, Optional
import requests
from pydantic import BaseModel,Field
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
    title = Column(String,nullable=True,default="Untitled Task")
    priority = Column(Enum(PriorityEnum),default=PriorityEnum.Medium)
    deadline = Column(String,nullable=True,default="No deadline")
    category = Column(String,nullable=True,default="General")
    notes = Column(String,nullable=True,default="")
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())


Base.metadata.create_all(engine)
class TaskDetails(BaseModel):
    title: str = Field(description="The title of the task.")
    priority: str = Field(description="Priority level: High, Medium, or Low.")
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
    url = "http://localhost:11434/api/chat"
    prompt = f"""
    You are an AI task organizer.  Take this task description and return a JSON with:
    title, priority (High, Medium, Low), category, deadline, notes.
    Task: {task_text}
    Return ONLY valid JSON, no additional text.
    """

    try:
        response = requests.post(url, json={
            "model": "gemma2:2b",
            "messages": [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': task_text}
            ],
            "stream": False  # Disable streaming for easier parsing
        })

        response.raise_for_status()
        data = response.json()

        # Ollama's response structure:  the content is in message. content
        content = data.get("message", {}).get("content", "").strip()

        # Extract and parse JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx + 1]
            parsed_data = json.loads(json_str)
            return parsed_data
        return {}
    except Exception as e:
        print(f"LLM error: {e}")
        return {}



@app.post("/task",response_model=ReadTask)
def create_task(task: CreateTask,db: Session = Depends(get_db)):
    refined_task = reform_with_llm(task.original_text)
    
    # Map priority string to PriorityEnum
    priority_str = refined_task.get("priority", "Medium")
    try:
        priority_enum = PriorityEnum[priority_str]
    except (KeyError, TypeError):
        priority_enum = PriorityEnum.Medium
    
    db_task = Task(
        original_text = task.original_text,
        title = refined_task.get("title", "Untitled Task"),
        priority = priority_enum,
        deadline = refined_task.get("deadline", "No deadline"),
        category = refined_task.get("category", "General"),
        notes = refined_task.get("notes", ""),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks",response_model=List[ReadTask])
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks









