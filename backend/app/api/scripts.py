from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pathlib import Path

from app.models import (
    Script,
    DialogueItem,
    MessageResponse,
    Task,
    TaskType,
    TaskStatus,
    ScriptResponse,
    DialogueResponse,
    DialogueAddResponse,
    DialogueDeleteResponse
)
from app.services.project_service import ProjectService
from app.services.script_service import ScriptService
from app.services.task_service import TaskService
from pydantic import BaseModel, Field

scripts_router = APIRouter(prefix="/api/scripts", tags=["scripts"])
dialogue_router = APIRouter(prefix="/api/dialogues", tags=["dialogues"])


# 请求模型
class ScriptGenerateRequest(BaseModel):
    """生成脚本请求"""
    project_id: str
    page_number: int = Field(..., ge=1, description="要生成脚本的页面页码")


class ScriptBatchGenerateRequest(BaseModel):
    """批量生成脚本请求"""
    project_id: str


class ScriptUpdateRequest(BaseModel):
    """更新脚本请求"""
    dialogues: List[DialogueItem]


class DialogueUpdateRequest(BaseModel):
    """更新对话项请求"""
    role: str
    content: str
    emotion: str
    speed: str


class DialogueAddRequest(BaseModel):
    """添加对话项请求"""
    role: str
    content: str
    emotion: str
    speed: str


class DialogueMoveRequest(BaseModel):
    """移动对话项请求"""
    direction: str = Field(..., pattern="^(up|down)$", description="移动方向：up-上移，down-下移")


class ScriptBatchGenerateResponse(BaseModel):
    """批量生成脚本响应"""
    message: str
    task_id: str


# 依赖注入：获取项目服务
def get_project_service() -> ProjectService:
    return ProjectService()


# 依赖注入：获取脚本服务
def get_script_service() -> ScriptService:
    return ScriptService()


# 依赖注入：获取任务服务
def get_task_service() -> TaskService:
    return TaskService()


async def batch_generate_scripts_task(project_id: str, task_id: str):
    """批量生成脚本的后台任务"""
    script_service = ScriptService()
    task_service = TaskService()
    
    try:
        # 获取项目信息
        project_service = ProjectService()
        project = project_service.get_project(project_id)
        if not project:
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message="项目不存在")
            return
        
        # 检查项目是否已转换PDF为图片
        if not project.images:
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message="项目未转换PDF为图片")
            return
        
        # 计算总页数
        total_pages = len(project.images)
        
        # 更新任务状态为运行中
        task_service.update_task_status(task_id, TaskStatus.RUNNING)
        
        # 批量生成脚本
        scripts = await script_service.batch_generate_scripts(project_id, task_id)
        
        # 更新任务状态为完成
        task_service.update_task_status(task_id, TaskStatus.COMPLETED, progress=1.0)
        
    except Exception as e:
        # 更新任务状态为失败
        task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))


@scripts_router.post("/batch-generate", response_model=ScriptBatchGenerateResponse)
async def batch_generate_scripts(
    request: ScriptBatchGenerateRequest,
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(get_project_service),
    task_service: TaskService = Depends(get_task_service)
):
    """批量生成脚本"""
    # 检查项目是否存在
    project = project_service.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查项目是否已转换PDF为图片
    if not project.images:
        raise HTTPException(status_code=400, detail="项目未转换PDF为图片")
    
    try:
        # 创建任务
        task = task_service.create_task(
            task_type=TaskType.SCRIPT_GENERATION,
            total_steps=len(project.images)
        )
        
        # 添加后台任务
        background_tasks.add_task(
            batch_generate_scripts_task,
            request.project_id,
            task.id
        )
        
        return ScriptBatchGenerateResponse(
            message="脚本生成已开始",
            task_id=task.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成脚本失败: {str(e)}")


@scripts_router.post("/generate", response_model=ScriptResponse)
async def generate_script_for_page(
    request: ScriptGenerateRequest,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """为指定页面生成脚本"""
    # 检查项目是否存在
    project = project_service.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查项目是否已转换PDF为图片
    if not project.images:
        raise HTTPException(status_code=400, detail="项目未转换PDF为图片")
    
    # 检查页码是否有效
    if request.page_number < 1 or request.page_number > len(project.images):
        raise HTTPException(status_code=400, detail=f"页码无效，有效范围为1-{len(project.images)}")
    
    # 检查前面的页面是否已生成脚本
    for i in range(1, request.page_number):
        existing_script = script_service.get_script(request.project_id, i)
        if not existing_script:
            raise HTTPException(status_code=400, detail=f"页面{i}的脚本尚未生成，请先生成前面的页面脚本")
    
    try:
        # 生成脚本
        script = await script_service.generate_script_for_page(request.project_id, request.page_number)
        return ScriptResponse(message="success", script=script)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成脚本失败: {str(e)}")


@scripts_router.get("/{project_id}/{page_number}", response_model=ScriptResponse)
async def get_script(
    project_id: str,
    page_number: int,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """获取指定页面的脚本"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查页码是否有效
    if page_number < 1:
        raise HTTPException(status_code=400, detail="页码必须大于0")
    
    try:
        # 获取脚本
        script = script_service.get_script(project_id, page_number)
        if not script:
            raise HTTPException(status_code=404, detail="脚本不存在")
        
        return ScriptResponse(message="success", script=script)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取脚本失败: {str(e)}")


@scripts_router.put("/{project_id}/{page_number}", response_model=ScriptResponse)
async def update_script(
    project_id: str,
    page_number: int,
    request: ScriptUpdateRequest,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """更新脚本"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 更新脚本
        script = script_service.update_script_by_page_number(project_id, page_number, request.dialogues)
        if not script:
            raise HTTPException(status_code=404, detail="脚本不存在")
        
        return ScriptResponse(message="success", script=script)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新脚本失败: {str(e)}")


@dialogue_router.put("/{project_id}/{page_number}/{dialogue_id}", response_model=DialogueResponse)
async def update_dialogue(
    project_id: str,
    page_number: int,
    dialogue_id: str,
    request: DialogueUpdateRequest,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """更新对话项"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 更新对话项
        dialogue = script_service.update_dialogue_by_id(project_id, page_number, dialogue_id, 
                                                      role=request.role,
                                                      content=request.content,
                                                      emotion=request.emotion,
                                                      speed=request.speed)
        if not dialogue:
            raise HTTPException(status_code=404, detail="对话项不存在")
        
        return DialogueResponse(message="success", dialogue=dialogue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新对话项失败: {str(e)}")


@dialogue_router.post("/{project_id}/{page_number}", response_model=DialogueAddResponse)
async def add_dialogue(
    project_id: str,
    page_number: int,
    request: DialogueAddRequest,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """添加对话项"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 添加对话项
        dialogue = script_service.add_dialogue_to_page(project_id, page_number, 
                                                     role=request.role,
                                                     content=request.content,
                                                     emotion=request.emotion,
                                                     speed=request.speed)
        if not dialogue:
            raise HTTPException(status_code=404, detail="脚本不存在")
        
        # 获取脚本ID
        script = script_service.get_script(project_id, page_number)
        script_id = script.id if script else ""
        return DialogueAddResponse(
            id=dialogue.id,
            script_id=script_id,
            role=dialogue.role,
            content=dialogue.content,
            emotion=dialogue.emotion,
            speed=dialogue.speed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加对话项失败: {str(e)}")


@dialogue_router.delete("/{project_id}/{page_number}/{dialogue_id}", response_model=DialogueDeleteResponse)
async def delete_dialogue(
    project_id: str,
    page_number: int,
    dialogue_id: str,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """删除对话项"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 删除对话项
        dialogue = script_service.delete_dialogue_by_id(project_id, page_number, dialogue_id)
        if not dialogue:
            raise HTTPException(status_code=404, detail="对话项不存在")
        
        return DialogueDeleteResponse(message="success", dialogue=dialogue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除对话项失败: {str(e)}")


@dialogue_router.put("/{project_id}/{page_number}/{dialogue_id}/move", response_model=DialogueResponse)
async def move_dialogue(
    project_id: str,
    page_number: int,
    dialogue_id: str,
    request: DialogueMoveRequest,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service)
):
    """移动对话项"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        # 移动对话项
        dialogue = script_service.move_dialogue_by_id(project_id, page_number, dialogue_id, request.direction)
        if not dialogue:
            raise HTTPException(status_code=404, detail="对话项不存在或移动失败")
        
        return DialogueResponse(message="success", dialogue=dialogue)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移动对话项失败: {str(e)}")