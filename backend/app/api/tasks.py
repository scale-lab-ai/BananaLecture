from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.models import (
    Task,
    TaskType,
    TaskStatus,
    MessageResponse
)
from app.services.task_service import TaskService
from pydantic import BaseModel

tasks_router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# 请求模型
class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    type: TaskType
    total_steps: int = 0


class TaskStatusUpdateRequest(BaseModel):
    """更新任务状态请求"""
    status: TaskStatus
    progress: Optional[float] = None
    current_step: Optional[int] = None
    error_message: Optional[str] = None


class TaskProgressResponse(BaseModel):
    """任务进度响应"""
    finished: bool
    task: Task


# 依赖注入：获取任务服务
def get_task_service() -> TaskService:
    return TaskService()


@tasks_router.post("", response_model=Task)
async def create_task(
    request: TaskCreateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """创建新任务"""
    try:
        task = task_service.create_task(
            task_type=request.type,
            total_steps=request.total_steps
        )
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@tasks_router.get("/{task_id}", response_model=TaskProgressResponse)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    """获取任务状态"""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 判断任务是否完成
    finished = task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    
    return TaskProgressResponse(finished=finished, task=task)


@tasks_router.put("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: str,
    request: TaskStatusUpdateRequest,
    task_service: TaskService = Depends(get_task_service)
):
    """更新任务状态"""
    success = task_service.update_task_status(
        task_id=task_id,
        status=request.status,
        progress=request.progress,
        current_step=request.current_step,
        error_message=request.error_message
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_service.get_task(task_id)
    return task


@tasks_router.post("/{task_id}/progress", response_model=Task)
async def increment_task_progress(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    """增加任务进度"""
    success = task_service.increment_task_progress(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_service.get_task(task_id)
    return task


@tasks_router.delete("/{task_id}", response_model=MessageResponse)
async def cancel_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
):
    """取消任务"""
    success = task_service.cancel_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无法取消")
    
    return MessageResponse(message="canceled")


@tasks_router.get("", response_model=List[Task])
async def get_all_tasks(
    task_type: Optional[TaskType] = None,
    task_service: TaskService = Depends(get_task_service)
):
    """获取所有任务"""
    if task_type:
        return task_service.get_tasks_by_type(task_type)
    else:
        return task_service.get_all_tasks()


@tasks_router.get("/running/list", response_model=List[Task])
async def get_running_tasks(
    task_service: TaskService = Depends(get_task_service)
):
    """获取正在运行的任务"""
    return task_service.get_running_tasks()