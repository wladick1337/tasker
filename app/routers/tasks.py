from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.schemas import TaskCreate, TaskPublic, TaskUpdate

from app import models
from app.models import TaskPriority, TaskStatus

router = APIRouter()

@router.post(
    "",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    )
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
        ):

    new_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("", response_model=list[TaskPublic])
def get_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    query = select(models.Task)

    if status:
        query = query.where(models.Task.status == status)

    if priority:
        query = query.where(models.Task.priority == priority)

    offset = (page - 1) * limit

    query = query.order_by(models.Task.id).offset(offset).limit(limit)

    result = db.execute(query)
    tasks = result.scalars().all()

    return tasks

@router.get("/{task_id}", response_model=TaskPublic)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):

    result = db.execute(select(models.Task).where(models.Task.id == task_id))

    task = result.scalars().first()

    if task:
        return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    
):
    result = db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    result = db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
    return None