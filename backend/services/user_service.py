from sqlalchemy.orm import Session
from database import User, Roadmap, Task, TaskFailure
from schemas.users import UserCreate, RoadmapResponse, TaskResponse, TasksResponse
from services.llm_service import LLMService
from services.sources_api_service import SourcesAPIService, MockSourcesAPIService
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import uuid
import os

class UserService:
    def __init__(self):
        self.llm_service = LLMService()
        
        # Initialize sources API service
        # Check if we should use mock or real API
        sources_api_url = os.getenv("SOURCES_API_URL")
        if sources_api_url:
            self.sources_service = SourcesAPIService(sources_api_url)
        else:
            # Use mock service for testing
            self.sources_service = MockSourcesAPIService()
            print("Using mock sources API service")
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            name=user_data.name,
            age=user_data.age,
            time_duration=user_data.time_duration,
            interests=user_data.interests
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def generate_roadmap(self, db: Session, user_id: int) -> RoadmapResponse:
        """Generate a new roadmap for the user"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Deactivate previous roadmaps
        db.query(Roadmap).filter(Roadmap.user_id == user_id).update({"is_active": False})
        
        # Generate new roadmap using LLM
        roadmap_data = self.llm_service.generate_roadmap(
            user.interests, 
            user.time_duration, 
            user.age
        )
        
        # Create roadmap in database
        roadmap = Roadmap(
            user_id=user_id,
            title=roadmap_data["title"],
            steps=roadmap_data["steps"],
            is_active=True
        )
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)

        # Also generate initial tasks for step 1 and store them (do not return)
        try:
            _ = self._generate_and_store_tasks_for_current_step(db, user, roadmap)
            db.commit()
        except Exception:
            db.rollback()
        
        return RoadmapResponse(
            id=roadmap.id,
            title=roadmap.title,
            steps=roadmap.steps,
            created_at=roadmap.created_at,
            is_active=roadmap.is_active
        )
    
    def get_active_roadmap(self, db: Session, user_id: int) -> Optional[RoadmapResponse]:
        """Get the active roadmap for a user"""
        roadmap = db.query(Roadmap).filter(
            Roadmap.user_id == user_id,
            Roadmap.is_active == True
        ).first()
        
        if not roadmap:
            return None
        
        return RoadmapResponse(
            id=roadmap.id,
            title=roadmap.title,
            steps=roadmap.steps,
            created_at=roadmap.created_at,
            is_active=roadmap.is_active
        )
    
    def generate_tasks(self, db: Session, user_id: int) -> TasksResponse:
        """Generate tasks for the user based on their active roadmap and current step"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        roadmap = db.query(Roadmap).filter(
            Roadmap.user_id == user_id,
            Roadmap.is_active == True
        ).first()
        
        if not roadmap:
            raise ValueError("No active roadmap found. Please generate a roadmap first.")
        
        previous_failures = db.query(TaskFailure.failure_reason).filter(
            TaskFailure.user_id == user_id
        ).order_by(TaskFailure.failure_date.desc()).limit(5).all()
        failure_reasons = [failure[0] for failure in previous_failures]
        
        current_step_num = getattr(roadmap, 'current_step', 1) or 1
        step = None
        for s in roadmap.steps:
            if isinstance(s, dict) and s.get("step_num") == current_step_num:
                step = s
                break
        if step is None and roadmap.steps:
            idx = min(max(current_step_num - 1, 0), len(roadmap.steps) - 1)
            step = roadmap.steps[idx]
        step_title = step.get("title") if isinstance(step, dict) else str(step)
        tasks_data = self.llm_service.generate_tasks(
            roadmap_step=step_title,
            user_interests=user.interests,
            time_duration=user.time_duration,
            previous_failures=failure_reasons,
            all_steps=roadmap.steps,
            current_step_num=current_step_num
        )
        
        tasks = []
        assigned_time = datetime.now(timezone.utc)
        created_task_objs = []
        for task_data in tasks_data:
            task = Task(
                user_id=user_id,
                roadmap_id=roadmap.id,
                step_num=current_step_num,
                title=task_data["title"],
                description=task_data["description"],
                assigned_time=assigned_time,
                sources=task_data.get("sources", []),  # Use sources from LLM
                completed=False
            )
            db.add(task)
            db.flush()
            created_task_objs.append(task)
            tasks.append(TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                assigned_time=task.assigned_time,
                sources=task.sources,
                completed=False
            ))
        
        db.commit()
        return TasksResponse(tasks=tasks)

    def _generate_and_store_tasks_for_current_step(self, db: Session, user: User, roadmap: Roadmap) -> List[Task]:
        """Internal: generate tasks for current step and store; returns Task list."""
        current_step_num = getattr(roadmap, 'current_step', 1) or 1
        step = None
        for s in roadmap.steps:
            if isinstance(s, dict) and s.get("step_num") == current_step_num:
                step = s
                break
        if step is None and roadmap.steps:
            idx = min(max(current_step_num - 1, 0), len(roadmap.steps) - 1)
            step = roadmap.steps[idx]
        step_title = step.get("title") if isinstance(step, dict) else str(step)
        previous_failures = db.query(TaskFailure.failure_reason).filter(
            TaskFailure.user_id == user.id
        ).order_by(TaskFailure.failure_date.desc()).limit(5).all()
        failure_reasons = [failure[0] for failure in previous_failures]
        tasks_data = self.llm_service.generate_tasks(
            roadmap_step=step_title,
            user_interests=user.interests,
            time_duration=user.time_duration,
            previous_failures=failure_reasons,
            all_steps=roadmap.steps,
            current_step_num=current_step_num
        )
        assigned_time = datetime.now(timezone.utc)
        created_tasks: List[Task] = []
        for td in tasks_data:
            t = Task(
                user_id=user.id,
                roadmap_id=roadmap.id,
                step_num=current_step_num,
                title=td["title"],
                description=td["description"],
                assigned_time=assigned_time,
                sources=td.get("sources", []),  # Use sources from LLM
                completed=False
            )
            db.add(t)
            db.flush()
            created_tasks.append(t)
        db.commit()
        return created_tasks
    
    def get_user_tasks(self, db: Session, user_id: int) -> TasksResponse:
        """Get all active incomplete tasks for a user"""
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_active == True,
            Task.completed == False
        ).all()
        
        task_responses = [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                assigned_time=task.assigned_time,
                sources=getattr(task, 'sources', []),
                completed=task.completed
            )
            for task in tasks
        ]
        
        return TasksResponse(tasks=task_responses)
    
    def handle_task_completion(self, db: Session, user_id: int, completed_tasks: List) -> dict:
        """Handle task completion and determine next steps"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update completed tasks
        completed_count = 0
        total_tasks = 0
        
        for task_completion in completed_tasks:
            task_id = task_completion.task_id if hasattr(task_completion, 'task_id') else task_completion["task_id"]
            completed = task_completion.completed if hasattr(task_completion, 'completed') else task_completion["completed"]
            
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if task:
                total_tasks += 1
                if completed:
                    task.completed = True
                    task.completed_at = datetime.now(timezone.utc)
                    completed_count += 1
        
        db.commit()
        
        # Check if all tasks for current step are completed
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.is_active == True).first()
        if roadmap:
            current_step_num = getattr(roadmap, 'current_step', 1) or 1
            remaining = db.query(Task).filter(
                Task.user_id == user_id,
                Task.roadmap_id == roadmap.id,
                Task.step_num == current_step_num,
                Task.completed == False,
                Task.is_active == True
            ).count()
            if remaining == 0:
                # advance step or finish roadmap
                total_steps = len(roadmap.steps) if roadmap.steps else 0
                if current_step_num >= total_steps:
                    # Finish roadmap
                    roadmap.is_active = False
                    db.commit()
                    return {"status": "roadmap_completed", "message": "Congratulations! You have completed the roadmap."}
                else:
                    roadmap.current_step = current_step_num + 1
                    # Auto-generate next step tasks and return them
                    user = self.get_user_by_id(db, user_id)
                    tasks_created = self._generate_and_store_tasks_for_current_step(db, user, roadmap)
                    db.commit()
                    task_responses = [
                        TaskResponse(
                            id=t.id,
                            title=t.title,
                            description=t.description,
                            assigned_time=t.assigned_time,
                            sources=t.sources,
                            completed=t.completed
                        ) for t in tasks_created
                    ]
                    return {"tasks": [tr.model_dump() for tr in task_responses]}
        
        # If not all current-step tasks completed
        if completed_count == total_tasks and total_tasks > 0:
            # Generate next tasks without step change (keep current step if remaining exist)
            tasks = self.get_user_tasks(db, user_id)
            return {"status": "all_completed", "message": "All submitted tasks marked as completed.", "tasks": tasks.model_dump()}
        elif completed_count > 0:
            # Some tasks completed - continue with remaining tasks
            return {"status": "partial_completion", "message": f"Completed {completed_count}/{total_tasks} tasks. Keep going!"}
        else:
            # No tasks completed - tasks will be handled by failure endpoint
            return {"status": "no_completion", "message": "No tasks were completed."}
    
    def handle_task_failure(self, db: Session, user_id: int, failure_reason: str, 
                          completed_tasks: List) -> TasksResponse:
        """Handle task failure and reassign tasks"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Count completed tasks
        completed_count = 0
        total_tasks = 0
        
        for task_completion in completed_tasks:
            task_id = task_completion.task_id if hasattr(task_completion, 'task_id') else task_completion["task_id"]
            completed = task_completion.completed if hasattr(task_completion, 'completed') else task_completion["completed"]
            
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if task:
                total_tasks += 1
                if completed:
                    task.completed = True
                    task.completed_at = datetime.now(timezone.utc)
                    completed_count += 1
        
        # Record the failure
        task_failure = TaskFailure(
            user_id=user_id,
            task_id=1,  # We'll use a placeholder since this is a general failure
            failure_reason=failure_reason,
            tasks_completed_count=completed_count,
            total_tasks_count=total_tasks
        )
        db.add(task_failure)
        
        # Get incomplete tasks
        incomplete_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_active == True,
            Task.completed == False
        ).all()
        
        # Get previous failure reasons for context
        previous_failures = db.query(TaskFailure.failure_reason).filter(
            TaskFailure.user_id == user_id
        ).order_by(TaskFailure.failure_date.desc()).limit(5).all()
        
        failure_reasons = [failure[0] for failure in previous_failures]
        
        if completed_count == 0:
            # No tasks completed - extend time and reassign all tasks
            assigned_time = datetime.now(timezone.utc)  # Current time
            
            # Convert incomplete tasks to dict format for LLM
            incomplete_tasks_data = [
                {"title": task.title, "description": task.description}
                for task in incomplete_tasks
            ]
            
            # Reassign tasks with more detail
            reassigned_tasks = self.llm_service.reassign_tasks(
                incomplete_tasks_data,
                failure_reason,
                user.interests,
                user.time_duration,
                failure_reasons
            )
            
            # Update existing tasks and create new ones
            tasks = []
            for i, task_data in enumerate(reassigned_tasks):
                if i < len(incomplete_tasks):
                    # Update existing task
                    task = incomplete_tasks[i]
                    task.title = task_data["title"]
                    task.description = task_data["description"]
                    task.assigned_time = assigned_time
                else:
                    # Create new task
                    task_id = f"task_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid.uuid4().hex[:8]}"
                    roadmap = db.query(Roadmap).filter(
                        Roadmap.user_id == user_id,
                        Roadmap.is_active == True
                    ).first()
                    
                    task = Task(
                        user_id=user_id,
                        roadmap_id=roadmap.id,
                        step_num=getattr(roadmap, 'current_step', 1) or 1,
                        title=task_data["title"],
                        description=task_data["description"],
                        assigned_time=assigned_time,
                        sources=task_data.get("sources", []),
                        completed=False
                    )
                    db.add(task)
                
                tasks.append(TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    assigned_time=assigned_time,
                    completed=False
                ))
        else:
            # Some tasks completed - reassign incomplete tasks with more detail
            assigned_time = datetime.now(timezone.utc)
            
            # Convert incomplete tasks to dict format for LLM
            incomplete_tasks_data = [
                {"title": task.title, "description": task.description}
                for task in incomplete_tasks
            ]
            
            # Reassign tasks with more detail
            reassigned_tasks = self.llm_service.reassign_tasks(
                incomplete_tasks_data,
                failure_reason,
                user.interests,
                user.time_duration,
                failure_reasons
            )
            
            # Update tasks
            tasks = []
            for i, task_data in enumerate(reassigned_tasks):
                if i < len(incomplete_tasks):
                    task = incomplete_tasks[i]
                    task.title = task_data["title"]
                    task.description = task_data["description"]
                    task.assigned_time = assigned_time
                    
                    tasks.append(TaskResponse(
                        id=task.id,
                        title=task.title,
                        description=task.description,
                        assigned_time=assigned_time,
                        sources=getattr(task, 'sources', []),
                        completed=False
                    ))
        
        db.commit()
        # Return only incomplete tasks (improved). If none left, generate next step tasks and return.
        remaining = db.query(Task).filter(Task.user_id == user_id, Task.completed == False, Task.is_active == True).all()
        if remaining:
            resp = [
                TaskResponse(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    assigned_time=t.assigned_time,
                    sources=getattr(t, 'sources', []),
                    completed=t.completed
                ) for t in remaining
            ]
            return TasksResponse(tasks=resp)
        # else generate next tasks
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.is_active == True).first()
        if roadmap:
            user = self.get_user_by_id(db, user_id)
            created = self._generate_and_store_tasks_for_current_step(db, user, roadmap)
            db.commit()
            return TasksResponse(tasks=[
                TaskResponse(id=t.id, title=t.title, description=t.description, assigned_time=t.assigned_time, sources=t.sources, completed=t.completed)
                for t in created
            ])
        return TasksResponse(tasks=[])
