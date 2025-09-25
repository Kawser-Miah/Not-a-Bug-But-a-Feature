from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# User Registration Schema
class UserCreate(BaseModel):
    name: str
    age: int
    time_duration: int  # minutes per day
    interests: List[str]

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    time_duration: int
    interests: List[str]
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat().replace('+00:00', 'Z') if v.tzinfo else v.isoformat() + 'Z'
        }

# Roadmap Schemas
class RoadmapStep(BaseModel):
    step_num: int
    title: str

class RoadmapResponse(BaseModel):
    id: int
    title: str
    steps: List[RoadmapStep]
    created_at: datetime
    is_active: bool

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat().replace('+00:00', 'Z') if v.tzinfo else v.isoformat() + 'Z'
        }

# Task Schemas
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    assigned_time: datetime
    sources: List[str] = []
    completed: bool

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat().replace('+00:00', 'Z') if v.tzinfo else v.isoformat() + 'Z'
        }

class TasksResponse(BaseModel):
    tasks: List[TaskResponse]

# Task Completion Schema
class TaskCompletion(BaseModel):
    task_id: int
    completed: bool

class TaskCompletionRequest(BaseModel):
    completed_tasks: List[TaskCompletion]

# Task Failure Schema
class TaskFailureRequest(BaseModel):
    failure_reason: str
    completed_tasks: List[TaskCompletion]

# Roadmap Generation Request
class RoadmapGenerationRequest(BaseModel):
    user_id: int
