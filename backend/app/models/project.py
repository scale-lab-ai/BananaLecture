from typing import Optional, List
from pydantic import Field, ConfigDict, BaseModel

from .base import BaseIdentifiedModel
from .dialogue import Script, DialogueItem


class Image(BaseIdentifiedModel):
    model_config = ConfigDict(use_enum_values=True)
    
    img_path: str = Field(..., description="图片路径")
    script: Optional[Script] = Field(None, description="关联的脚本")


class Project(BaseIdentifiedModel):
    model_config = ConfigDict(use_enum_values=True)
    
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    pdf_path: Optional[str] = Field(None, description="PDF文件路径")
    images: list[Image] = Field(default_factory=list, description="图片列表")


# 请求和响应模型
class ProjectCreateRequest(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")


class ProjectUpdateRequest(BaseModel):
    """更新项目请求"""
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")


class ProjectResponse(BaseModel):
    """项目响应"""
    id: str
    name: str
    pdf_path: Optional[str] = None
    created_at: str
    updated_at: str


class ProjectsListResponse(BaseModel):
    """项目列表响应"""
    projects: List[ProjectResponse]


class ProjectDetailResponse(BaseModel):
    """项目详情响应"""
    message: str = "success"
    project: Project


class MessageResponse(BaseModel):
    """消息响应"""
    message: str


class PDFUploadResponse(BaseModel):
    """PDF上传响应"""
    message: str
    pdf_path: str


class PDFConvertResponse(BaseModel):
    """PDF转换响应"""
    message: str
    images: List[Image]


class ScriptResponse(BaseModel):
    """脚本响应"""
    message: str = "success"
    script: Script


class DialogueResponse(BaseModel):
    """对话响应"""
    message: str = "success"
    dialogue: DialogueItem


class DialogueAddResponse(BaseModel):
    """对话添加响应"""
    id: str
    script_id: str
    role: str
    content: str
    emotion: str
    speed: str


class DialogueDeleteResponse(BaseModel):
    """对话删除响应"""
    message: str = "success"
    dialogue: DialogueItem