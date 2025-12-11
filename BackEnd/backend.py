import datetime
import enum
import json
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
    title = Column(String,nullable=True,default="Untitled Task")
    priority = Column(Enum(PriorityEnum),default=PriorityEnum.Medium)
    deadline = Column(String,nullable=True,default="No deadline")
    category = Column(String,nullable=True,default="General")
    notes = Column(String,nullable=True,default="")
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


def _get_default_task_data(task_text: str) -> dict:
    """
    Fallback function that returns default task data when LLM parsing fails.
    Uses the original task text as the title.
    """
    print(f"[DEBUG] Creating default task data for: {task_text[:50]}...")
    return {
        "title": task_text[:100] if len(task_text) <= 100 else task_text[:97] + "...",
        "priority": "Medium",
        "category": "General",
        "deadline": "No deadline",
        "notes": "Created with fallback values due to LLM parsing failure"
    }


def reform_with_llm(task_text: str) -> dict:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    # Debug: Log API key status (masked for security)
    if GROQ_API_KEY:
        print(f"[DEBUG] API key found: {GROQ_API_KEY[:8]}...{GROQ_API_KEY[-4:] if len(GROQ_API_KEY) > 12 else '****'}")
    else:
        print("[DEBUG] WARNING: No API key found in environment!")
    
    prompt = f"""
        You are an AI task organizer, Take this task description and return a JSON with:
        title,priority(High,Medium,Low),category,deadline,notes.
        Task: {task_text}
        Return ONLY valid JSON, no additional text.
        """
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 100
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"[DEBUG] Making API request to {GROQ_API_URL}")
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        
        # Debug: Log response status
        print(f"[DEBUG] Response status code: {response.status_code}")
        print(f"[DEBUG] Raw response: {response.text[:500]}...")  # First 500 chars
        
        response.raise_for_status()
        results = response.json()
        
        # Debug: Log the full response structure
        print(f"[DEBUG] Response JSON structure: {json.dumps(results, indent=2)[:500]}...")
        
        # Extract the content from the OpenAI-compatible response
        content = results.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Debug: Log extracted content
        print(f"[DEBUG] Extracted content: {content}")
        
        # Parse the JSON content
        if content:
            # Try to extract JSON from the content (in case there's extra text)
            content = content.strip()
            # Find JSON object in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx+1]
                print(f"[DEBUG] Extracted JSON string: {json_str}")
                parsed_data = json.loads(json_str)
                print(f"[DEBUG] Successfully parsed data: {parsed_data}")
                return parsed_data
            else:
                print("[DEBUG] ERROR: No JSON object found in content")
                print("[DEBUG] Falling back to default values")
                return _get_default_task_data(task_text)
        else:
            print("[DEBUG] ERROR: Empty content received from API")
            print("[DEBUG] Falling back to default values")
            return _get_default_task_data(task_text)
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] API request error: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        print("[DEBUG] Falling back to default values")
        return _get_default_task_data(task_text)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parsing error: {e}")
        print(f"[DEBUG] Failed to parse: {content if 'content' in locals() else 'N/A'}")
        print("[DEBUG] Falling back to default values")
        return _get_default_task_data(task_text)
    except Exception as e:
        print(f"[DEBUG] Unexpected error: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        print("[DEBUG] Falling back to default values")
        return _get_default_task_data(task_text)


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









