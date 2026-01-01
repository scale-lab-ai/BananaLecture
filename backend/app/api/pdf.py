from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from typing import List
from pathlib import Path

from app.models import (
    Image,
    MessageResponse,
    PDFConvertResponse
)
from app.services.project_service import ProjectService
from app.services.pdf_service import PDFService

pdf_router = APIRouter(prefix="/api", tags=["pdf"])


# 依赖注入：获取项目服务
def get_project_service() -> ProjectService:
    return ProjectService()


# 依赖注入：获取PDF服务
def get_pdf_service() -> PDFService:
    return PDFService()


@pdf_router.post("/projects/{project_id}/convert-pdf", response_model=PDFConvertResponse)
async def convert_pdf_to_images(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """将PDF转换为图片"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查项目是否已上传PDF
    if not project.pdf_path:
        raise HTTPException(status_code=400, detail="项目未上传PDF文件")
    
    try:
        # 转换PDF为图片
        images = pdf_service.convert_pdf_to_images(project_id, project.pdf_path)
        
        # 更新项目信息
        project.images = images
        project_service._save_project_data(project)
        
        return PDFConvertResponse(
            message="PDF转换成功",
            images=images
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")


@pdf_router.get("/images/{project_id}/{page_number}")
async def get_image_file(
    project_id: str,
    page_number: int,
    project_service: ProjectService = Depends(get_project_service),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """获取指定项目的指定页面图片文件"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 检查项目是否已转换PDF为图片
    if not project.images or len(project.images) == 0:
        raise HTTPException(status_code=400, detail="项目未转换PDF为图片")
    
    # 检查页码是否有效
    if page_number < 1 or page_number > len(project.images):
        raise HTTPException(status_code=400, detail=f"页码无效，有效范围为1-{len(project.images)}")
    
    # 使用服务层方法获取图片路径
    image_path = pdf_service.get_image_path(project_id, page_number)
    if not image_path:
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    # 返回图片文件
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        filename=f"page_{page_number:03d}.png"
    )