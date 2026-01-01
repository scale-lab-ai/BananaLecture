from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional

from app.models import (
    Project,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectsListResponse,
    ProjectDetailResponse,
    MessageResponse,
    PDFUploadResponse
)
from app.services.project_service import ProjectService
from app.utils.file_utils import save_upload_file, validate_file_type

projects_router = APIRouter(prefix="/api/projects", tags=["projects"])


# 依赖注入：获取项目服务
def get_project_service() -> ProjectService:
    return ProjectService()


@projects_router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    request: ProjectCreateRequest,
    service: ProjectService = Depends(get_project_service)
):
    """创建项目"""
    try:
        project = service.create_project(request.name)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            pdf_path=project.pdf_path,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")



@projects_router.post("/{project_id}/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(
    project_id: str,
    pdf_file: UploadFile = File(...),
    service: ProjectService = Depends(get_project_service)
):
    """上传PDF文件"""
    # 验证文件类型
    if not validate_file_type(pdf_file.filename, ["pdf"]):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    try:
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        pdf_path = service.upload_pdf(project_id, pdf_file)
        return PDFUploadResponse(
            message="PDF文件上传成功",
            pdf_path=pdf_path
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传PDF文件失败: {str(e)}")


@projects_router.get("", response_model=ProjectsListResponse)
async def get_projects(
    service: ProjectService = Depends(get_project_service)
):
    """获取项目列表"""
    try:
        projects = service.get_all_projects()
        project_responses = [
            ProjectResponse(
                id=project.id,
                name=project.name,
                pdf_path=project.pdf_path,
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat()
            )
            for project in projects
        ]
        return ProjectsListResponse(projects=project_responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")



@projects_router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """获取项目详情"""
    try:
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return ProjectDetailResponse(
            message="success",
            project=project
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目详情失败: {str(e)}")

@projects_router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    service: ProjectService = Depends(get_project_service)
):
    """更新项目名称"""
    try:
        project = service.update_project(project_id, request.name)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return ProjectResponse(
            id=project.id,
            name=project.name,
            pdf_path=project.pdf_path,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新项目失败: {str(e)}")



@projects_router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service)
):
    """删除项目"""
    try:
        success = service.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        return MessageResponse(message=f"删除项目 {project_id} 成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除项目失败: {str(e)}")