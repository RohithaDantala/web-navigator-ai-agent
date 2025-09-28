# models/task_models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskStep(BaseModel):
    step_type: str
    target: str
    action: str
    value: Optional[str] = None
    data_fields: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = {}

class TaskPlan(BaseModel):
    task_id: str
    instruction: str
    steps: List[TaskStep]
    status: TaskStatus = TaskStatus.PENDING
    created_at: str
    estimated_duration: Optional[int] = None

class TaskResult(BaseModel):
    task_id: str
    success: bool
    data: List[Dict[str, Any]]
    execution_time: float
    pages_visited: List[str]
    error: Optional[str] = None