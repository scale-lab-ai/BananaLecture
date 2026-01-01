from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.services.project_service import ProjectService
from app.services.export_service import ExportService
from app.models.project import MessageResponse

logger = logging.getLogger(__name__)

export_router = APIRouter(prefix="/api", tags=["export"])


# 依赖注入：获取项目服务
def get_project_service() -> ProjectService:
    return ProjectService()


# 依赖注入：获取导出服务
def get_export_service() -> ExportService:
    return ExportService()


@export_router.get("/projects/{project_id}/download-ppt", response_class=FileResponse)
async def download_ppt(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
    export_service: ExportService = Depends(get_export_service)
):
    """导出并下载PPT
    
    Args:
        project_id: 项目ID
        
    Returns:
        PPT文件流
        
    Raises:
        HTTPException: 当项目不存在或缺少必要文件时抛出404或400错误
    """
    try:
        # 检查项目是否存在
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 检查项目是否有图片
        if not project.images:
            raise HTTPException(status_code=400, detail="项目未转换PDF为图片")
        
        # 导出PPT
        ppt_path = export_service.export_ppt(project_id)
        
        if not ppt_path.exists():
            raise HTTPException(status_code=404, detail="PPT文件生成失败")
        
        # 获取文件名（用于下载时的文件名）
        download_filename = ppt_path.name
        
        logger.info(f"项目 {project_id} 导出PPT成功: {ppt_path}")
        
        # 返回文件流
        return FileResponse(
            path=str(ppt_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=download_filename,
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"导出PPT失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出PPT失败: {str(e)}")