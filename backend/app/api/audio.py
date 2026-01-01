from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, Response
from typing import List, Optional
from pathlib import Path

from app.models import (
    DialogueItem,
    Task,
    TaskType,
    TaskStatus
)
from app.services.project_service import ProjectService
from app.services.script_service import ScriptService
from app.services.audio_service import AudioService
from app.services.task_service import TaskService
from pydantic import BaseModel, Field

audio_router = APIRouter(prefix="/api/audio", tags=["audio"])


# 请求模型
class AudioBatchGenerateRequest(BaseModel):
    """批量生成音频请求"""
    project_id: str


class AudioPageGenerateRequest(BaseModel):
    """页面生成音频请求"""
    project_id: str
    page_number: int = Field(..., ge=1, description="要生成音频的页面页码")


class AudioDialogueGenerateRequest(BaseModel):
    """对话生成音频请求"""
    project_id: str
    page_number: int = Field(..., ge=1, description="对话所在页面页码")
    dialogue_id: str


class AudioTaskResponse(BaseModel):
    """音频生成响应"""
    message: str
    task_id: str

class AudioGenerateResponse(BaseModel):
    """音频生成响应"""
    message: str
    dialogue: DialogueItem


# 依赖注入：获取项目服务
def get_project_service() -> ProjectService:
    return ProjectService()


# 依赖注入：获取脚本服务
def get_script_service() -> ScriptService:
    return ScriptService()


# 依赖注入：获取音频服务
def get_audio_service() -> AudioService:
    return AudioService()


# 依赖注入：获取任务服务
def get_task_service() -> TaskService:
    return TaskService()


async def batch_generate_audio_task(project_id: str, task_id: str):
    """批量生成音频的后台任务"""
    async with AudioService() as audio_service:
        task_service = TaskService()
        
        try:
            # 获取项目信息
            project_service = ProjectService()
            project = project_service.get_project(project_id)
            if not project:
                task_service.update_task_status(task_id, TaskStatus.FAILED, error_message="项目不存在")
                return
            
            # 检查项目是否已生成脚本
            if not project.images:
                task_service.update_task_status(task_id, TaskStatus.FAILED, error_message="项目未转换PDF为图片")
                return
            
            # 检查脚本是否存在
            script_service = ScriptService()
            has_scripts = False
            for index, image in enumerate(project.images):
                # 从图片路径中提取页码，或者使用索引+1作为页码
                page_number = index + 1
                script = script_service.get_script(project_id, page_number)
                if script and script.dialogues:
                    has_scripts = True
                    break
            
            if not has_scripts:
                task_service.update_task_status(task_id, TaskStatus.FAILED, error_message="项目未生成脚本")
                return
            
            # 更新任务状态为运行中
            task_service.update_task_status(task_id, TaskStatus.RUNNING)
            
            # 批量生成音频
            audio_files = await audio_service.batch_generate_audio(project_id, task_id)
            
            # 更新任务状态为完成
            task_service.update_task_status(task_id, TaskStatus.COMPLETED, progress=1.0)
            
        except Exception as e:
            # 更新任务状态为失败
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))


async def page_generate_audio_task(project_id: str, page_number: int, task_id: str):
    """页面生成音频的后台任务"""
    async with AudioService() as audio_service:
        task_service = TaskService()
        
        try:
            # 获取项目信息
            project_service = ProjectService()
            project = project_service.get_project(project_id)
            if not project:
                task_service.update_task_status(task_id, TaskStatus.FAILED, error_message="项目不存在")
                return
            
            # 检查项目是否已生成脚本
            script_service = ScriptService()
            script = script_service.get_script(project_id, page_number)
            if not script or not script.dialogues:
                task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=f"页面{page_number}的脚本不存在或为空")
                return
            
            # 更新任务状态为运行中
            task_service.update_task_status(task_id, TaskStatus.RUNNING)
            
            # 生成页面音频
            audio_file = await audio_service.generate_audio_for_page(project_id, page_number, task_id)
            
            # 更新任务状态为完成
            task_service.update_task_status(task_id, TaskStatus.COMPLETED, progress=1.0)
            
        except Exception as e:
            # 更新任务状态为失败
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))



@audio_router.post("/batch-generate", response_model=AudioTaskResponse)
async def batch_generate_audio(
    request: AudioBatchGenerateRequest,
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(get_project_service),
    task_service: TaskService = Depends(get_task_service)
):
    """批量生成音频"""
    # 检查项目是否存在
    project = project_service.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查项目是否已转换PDF为图片
    if not project.images:
        raise HTTPException(status_code=400, detail="项目未转换PDF为图片")
    
    # 检查脚本是否存在
    script_service = ScriptService()
    has_scripts = False
    for index, image in enumerate(project.images):
        # 从图片路径中提取页码，或者使用索引+1作为页码
        page_number = index + 1
        script = script_service.get_script(request.project_id, page_number)
        if script and script.dialogues:
            has_scripts = True
            break
    
    if not has_scripts:
        raise HTTPException(status_code=400, detail="项目未生成脚本")
    
    try:
        # 创建任务
        task = task_service.create_task(
            task_type=TaskType.AUDIO_GENERATION,
            total_steps=len(project.images)
        )
        
        # 添加后台任务
        background_tasks.add_task(
            batch_generate_audio_task,
            request.project_id,
            task.id
        )
        
        return AudioTaskResponse(
            message="音频生成已开始",
            task_id=task.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成音频失败: {str(e)}")


@audio_router.post("/page/generate", response_model=AudioTaskResponse)
async def generate_audio_for_page(
    request: AudioPageGenerateRequest,
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service),
    task_service: TaskService = Depends(get_task_service)
):
    """为指定页面生成音频"""
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
    
    # 检查脚本是否存在
    script = script_service.get_script(request.project_id, request.page_number)
    if not script or not script.dialogues:
        raise HTTPException(status_code=400, detail=f"页面{request.page_number}的脚本不存在或为空")
    
    try:
        # 创建任务
        task = task_service.create_task(
            task_type=TaskType.AUDIO_GENERATION,
            total_steps=len(script.dialogues)
        )
        
        # 添加后台任务
        background_tasks.add_task(
            page_generate_audio_task,
            request.project_id,
            request.page_number,
            task.id
        )
        
        return AudioTaskResponse(
            message="音频生成已开始",
            task_id=task.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成页面音频失败: {str(e)}")

@audio_router.post("/dialogue/generate", response_model=AudioGenerateResponse)
async def generate_audio_for_dialogue(
    request: AudioDialogueGenerateRequest,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service),
    audio_service: AudioService = Depends(get_audio_service)
):
    """为指定对话生成音频"""
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
    
    # 检查脚本是否存在
    script = script_service.get_script(request.project_id, request.page_number)
    if not script:
        raise HTTPException(status_code=400, detail=f"页面{request.page_number}的脚本不存在")
    
    # 查找对话项
    dialogue = None
    for d in script.dialogues:
        if d.id == request.dialogue_id:
            dialogue = d
            break
    
    if not dialogue:
        raise HTTPException(status_code=404, detail=f"对话项{request.dialogue_id}不存在")
    
    try:
        # 直接同步生成音频
        async with audio_service:
            audio_file_path = await audio_service.generate_audio_for_dialogue(
                dialogue, request.project_id, request.page_number
            )
        
        return AudioGenerateResponse(
            message="success",
            dialogue=dialogue
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成对话音频失败: {str(e)}")


@audio_router.get("/{project_id}/{page_number}/file")
async def get_audio_file(
    project_id: str,
    page_number: int,
    project_service: ProjectService = Depends(get_project_service),
    audio_service: AudioService = Depends(get_audio_service)
):
    """获取页面音频文件"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 获取音频文件内容
    audio_content = audio_service.get_audio_file_path(project_id, page_number)
    if not audio_content:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    # 返回音频文件内容
    return Response(
        content=audio_content,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename=page_{page_number:03d}.mp3"}
    )


@audio_router.get("/{project_id}/{page_number}/{dialogue_id}/audio-file")
async def get_dialogue_audio_file(
    project_id: str,
    page_number: int,
    dialogue_id: str,
    project_service: ProjectService = Depends(get_project_service),
    script_service: ScriptService = Depends(get_script_service),
    audio_service: AudioService = Depends(get_audio_service)
):
    """获取对话音频文件"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查脚本是否存在
    script = script_service.get_script(project_id, page_number)
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    # 检查对话项是否存在
    dialogue_exists = False
    for d in script.dialogues:
        if d.id == dialogue_id:
            dialogue_exists = True
            break
    
    if not dialogue_exists:
        raise HTTPException(status_code=404, detail="对话项不存在")
    
    # 获取音频文件内容
    audio_content = audio_service.get_dialogue_audio_file_path(project_id, page_number, dialogue_id)
    if not audio_content:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    # 返回音频文件内容
    return Response(
        content=audio_content,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename={dialogue_id}.mp3"}
    )