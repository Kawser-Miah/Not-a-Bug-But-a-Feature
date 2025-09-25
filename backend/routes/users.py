from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, User, Task, Roadmap
from schemas.users import (
    UserCreate, UserResponse, RoadmapResponse, TasksResponse,
    TaskCompletionRequest, TaskFailureRequest, RoadmapGenerationRequest
)
from services.user_service import UserService
from typing import List

router = APIRouter()
user_service = UserService()

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = user_service.create_user(db, user_data)
        # Auto-generate roadmap and initial tasks (not returned) happens inside service
        user_service.generate_roadmap(db, user.id)
        return UserResponse(
            id=user.id,
            name=user.name,
            age=user.age,
            time_duration=user.time_duration,
            interests=user.interests,
            created_at=user.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        name=user.name,
        age=user.age,
        time_duration=user.time_duration,
        interests=user.interests,
        created_at=user.created_at
    )

@router.post("/roadmap/generate", response_model=RoadmapResponse)
def generate_roadmap(request: RoadmapGenerationRequest, db: Session = Depends(get_db)):
    """Generate a new roadmap for the user"""
    try:
        roadmap = user_service.generate_roadmap(db, request.user_id)
        return roadmap
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roadmap/{user_id}", response_model=RoadmapResponse)
def get_roadmap(user_id: int, db: Session = Depends(get_db)):
    """Get the active roadmap for a user"""
    roadmap = user_service.get_active_roadmap(db, user_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found")
    
    return roadmap

@router.post("/tasks/generate/{user_id}", response_model=TasksResponse)
def generate_tasks(user_id: int, db: Session = Depends(get_db)):
    """Generate tasks for the user"""
    try:
        tasks = user_service.generate_tasks(db, user_id)
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{user_id}", response_model=TasksResponse)
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    """Get all active tasks for a user"""
    tasks = user_service.get_user_tasks(db, user_id)
    return tasks

@router.post("/tasks/complete/{user_id}")
def complete_tasks(user_id: int, request: TaskCompletionRequest, db: Session = Depends(get_db)):
    """Handle task completion"""
    try:
        result = user_service.handle_task_completion(db, user_id, request.completed_tasks)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/failure/{user_id}", response_model=TasksResponse)
def handle_task_failure(user_id: int, request: TaskFailureRequest, db: Session = Depends(get_db)):
    """Handle task failure and reassign tasks"""
    try:
        tasks = user_service.handle_task_failure(
            db, user_id, request.failure_reason, request.completed_tasks
        )
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/roadmap/regenerate/{user_id}", response_model=RoadmapResponse)
def regenerate_roadmap(user_id: int, db: Session = Depends(get_db)):
    """Regenerate roadmap (deletes previous roadmap and tasks)"""
    try:
        # Deactivate all previous roadmaps and tasks
        db.query(Task).filter(Task.user_id == user_id).update({"is_active": False})
        db.query(Roadmap).filter(Roadmap.user_id == user_id).update({"is_active": False})
        db.commit()
        
        # Generate new roadmap
        roadmap = user_service.generate_roadmap(db, user_id)  # also generates initial tasks internally
        return roadmap
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
