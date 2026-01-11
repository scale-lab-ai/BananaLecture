from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, Response
from typing import List
from pathlib import Path
import logging

from app.models import (
    Image,
    MessageResponse,
    PDFConvertResponse,
    TaskType
)
from app.services.project_service import ProjectService
from app.services.pdf_service import PDFService
from app.services.task_service import TaskService
from pdf2image import pdfinfo_from_path

pdf_router = APIRouter(prefix="/api", tags=["pdf"])
logger = logging.getLogger(__name__)


# 依赖注入：获取项目服务
def get_project_service() -> ProjectService:
    return ProjectService()


# 依赖注入：获取PDF服务
def get_pdf_service() -> PDFService:
    return PDFService()


# 依赖注入：获取任务服务
def get_task_service() -> TaskService:
    return TaskService()


async def convert_pdf_task(project_id: str, pdf_path: str, task_id: str, task_service: TaskService, pdf_service: PDFService, project_service: ProjectService):
    """Background task to convert PDF to images with progress tracking"""
    try:
        # Convert PDF with progress tracking (now async)
        images = await pdf_service.convert_pdf_to_images_with_progress(
            project_id,
            pdf_path,
            task_id,
            task_service
        )

        # Update project with images
        project = project_service.get_project(project_id)
        if project:
            project.images = images
            project_service._save_project_data(project)
    except Exception as e:
        logger = task_service._tasks.get(task_id)
        if logger:
            logger.error(f"PDF conversion task failed: {str(e)}")
        raise


@pdf_router.post("/projects/{project_id}/convert-pdf", response_model=PDFConvertResponse)
async def convert_pdf_to_images(
    project_id: str,
    background_tasks: BackgroundTasks,
    project_service: ProjectService = Depends(get_project_service),
    pdf_service: PDFService = Depends(get_pdf_service),
    task_service: TaskService = Depends(get_task_service)
):
    """Convert PDF to images with progress tracking"""
    # Check if project exists
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if project has uploaded PDF
    if not project.pdf_path:
        raise HTTPException(status_code=400, detail="Project has no PDF file uploaded")

    try:
        # Get PDF page count first
        pdf_path = Path(project.pdf_path)
        pdf_info = pdfinfo_from_path(pdf_path.as_posix())
        total_pages = pdf_info['Pages']

        # Create task for PDF conversion with total steps
        task = task_service.create_task(
            task_type=TaskType.PDF_CONVERSION,
            total_steps=total_pages
        )

        # Add background task
        background_tasks.add_task(
            convert_pdf_task,
            project_id,
            project.pdf_path,
            task.id,
            task_service,
            pdf_service,
            project_service
        )

        return PDFConvertResponse(
            message="PDF conversion started",
            images=[],
            task_id=task.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start PDF conversion: {str(e)}")


@pdf_router.get("/images/{project_id}/{page_number}")
async def get_image_file(
    project_id: str,
    page_number: int,
    project_service: ProjectService = Depends(get_project_service),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """获取指定项目的指定页面WebP压缩图片（用于前端传输）
    
    向后兼容：如果WebP不存在，会自动从PNG转换生成
    """
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if not project.images or len(project.images) == 0:
        raise HTTPException(status_code=400, detail="项目未转换PDF为图片")

    if page_number < 1 or page_number > len(project.images):
        raise HTTPException(status_code=400, detail=f"页码无效，有效范围为1-{len(project.images)}")

    webp_path = pdf_service.get_webp_image_path(project_id, page_number)

    if not webp_path:
        webp_path = pdf_service.convert_png_to_webp(project_id, page_number)
        
        if not webp_path:
            raise HTTPException(status_code=404, detail="图片文件不存在")

    return FileResponse(
        path=str(webp_path),
        media_type="image/webp",
        filename=f"page_{page_number:03d}.webp"
    )