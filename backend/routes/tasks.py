from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Task
from typing import List
from collections import defaultdict
from datetime import timedelta

router = APIRouter()

@router.get("/api/task/history/{user_id}")
def get_task_history(user_id: int, db: Session = Depends(get_db)):
    completed_tasks = db.query(Task).filter(Task.user_id == user_id, Task.completed == True).all()
    if not completed_tasks:
        return []
    return [
        {
            "id": task.id,
            "title": task.title,
            "completed_at": task.completed_at
        }
        for task in completed_tasks
    ]

@router.get("/api/task/completed/{user_id}")
def get_completed_tasks(user_id: int, db: Session = Depends(get_db)):
    from collections import defaultdict
    completed_tasks = db.query(Task).filter(Task.user_id == user_id, Task.completed == True).all()
    if not completed_tasks:
        return []
    total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
    grouped = defaultdict(list)
    for task in completed_tasks:
        # Round completed_at to nearest second (remove microseconds)
        rounded_time = task.completed_at.replace(microsecond=0)
        grouped[rounded_time].append(task)
    result = []
    for completed_at, tasks in grouped.items():
        completed_count = len(tasks)
        ratio = completed_count / total_tasks if total_tasks else 0.0
        result.append({
            "completed_at": completed_at,
            "completed_tasks": completed_count,
            "completion_ratio": round(ratio, 1)
        })
    return result

@router.get("/api/task/completed_count/within_one_minute/{user_id}")
def get_completed_count_within_one_minute(user_id: int, db: Session = Depends(get_db)):
    # Get all completed tasks for user
    completed_tasks = db.query(Task).filter(Task.user_id == user_id, Task.completed == True).order_by(Task.completed_at).all()
    if not completed_tasks:
        return {"completed_within_one_minute": 0}
    # Find the earliest completed_at
    first_completed = completed_tasks[0].completed_at
    one_minute_later = first_completed + timedelta(minutes=1)
    count = sum(1 for task in completed_tasks if first_completed <= task.completed_at < one_minute_later)
    return {"completed_within_one_minute": count}

@router.get("/api/task/completed_count/per_minute/{user_id}")
def get_completed_count_per_minute(user_id: int, db: Session = Depends(get_db)):
    completed_tasks = db.query(Task).filter(Task.user_id == user_id, Task.completed == True).order_by(Task.completed_at).all()
    if not completed_tasks:
        return []
    buckets = []
    first_time = completed_tasks[0].completed_at
    last_time = completed_tasks[-1].completed_at
    current_start = first_time
    current_end = current_start + timedelta(minutes=1)
    while current_start <= last_time:
        count = sum(1 for task in completed_tasks if current_start <= task.completed_at < current_end)
        buckets.append({
            "minute_start": current_start,
            "minute_end": current_end,
            "completed_count": count
        })
        current_start = current_end
        current_end = current_start + timedelta(minutes=1)
    return buckets
