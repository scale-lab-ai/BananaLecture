import os
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import logging

from app.models import Project, Image
from app.utils.file_utils import (
    generate_unique_id, 
    create_project_directory, 
    delete_directory,
    save_upload_file,
    safe_filename
)

logger = logging.getLogger(__name__)


class ProjectService:
    """项目服务类"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """初始化项目服务
        
        Args:
            storage_dir: 存储目录，默认为当前工作目录下的storage/projects
        """
        if storage_dir is None:
            # 默认存储目录为项目根目录下的storage/projects
            self.storage_dir = Path.cwd() / "storage" / "projects"
        else:
            self.storage_dir = Path(storage_dir)
        
        # 确保存储目录存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 项目数据存储路径
        self.data_dir = self.storage_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    def _get_project_file_path(self, project_id: str) -> Path:
        """获取项目数据文件路径"""
        return self.data_dir / f"{project_id}.json"
    
    def _save_project_data(self, project: Project) -> bool:
        """保存项目数据到文件"""
        try:
            project_file = self._get_project_file_path(project.id)
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"保存项目数据失败: {str(e)}")
            return False
    
    def _load_project_data(self, project_id: str) -> Optional[Project]:
        """从文件加载项目数据"""
        try:
            project_file = self._get_project_file_path(project_id)
            if not project_file.exists():
                return None
            
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 确保images字段存在且为列表
            if 'images' not in data:
                data['images'] = []
            
            return Project(**data)
        except Exception as e:
            logger.error(f"加载项目数据失败: {str(e)}")
            return None
    
    def create_project(self, name: str) -> Project:
        """创建新项目
        
        Args:
            name: 项目名称
            
        Returns:
            创建的项目对象
        """
        # 生成唯一ID
        project_id = generate_unique_id()
        
        # 创建项目目录结构
        directories = create_project_directory(project_id, self.storage_dir)
        
        # 创建项目对象
        project = Project(
            id=project_id,
            name=name
        )
        
        # 保存项目数据
        if not self._save_project_data(project):
            raise Exception("保存项目数据失败")
        
        logger.info(f"创建项目成功: {project_id}")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目详情
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目对象，如果不存在则返回None
        """
        return self._load_project_data(project_id)
    
    def get_all_projects(self) -> List[Project]:
        """获取所有项目列表
        
        Returns:
            项目列表
        """
        projects = []
        
        # 遍历数据目录中的所有项目文件
        for project_file in self.data_dir.glob("*.json"):
            project_id = project_file.stem
            project = self._load_project_data(project_id)
            if project:
                projects.append(project)
        
        # 按创建时间倒序排序
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects
    
    def update_project(self, project_id: str, name: str) -> Optional[Project]:
        """更新项目名称
        
        Args:
            project_id: 项目ID
            name: 新的项目名称
            
        Returns:
            更新后的项目对象，如果不存在则返回None
        """
        project = self._load_project_data(project_id)
        if not project:
            return None
        
        # 更新项目名称和时间戳
        project.name = name
        project.update_timestamp()
        
        # 保存更新后的数据
        if not self._save_project_data(project):
            raise Exception("保存项目数据失败")
        
        logger.info(f"更新项目成功: {project_id}")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            是否删除成功
        """
        # 检查项目是否存在
        project = self._load_project_data(project_id)
        if not project:
            return False
        
        try:
            # 删除项目目录
            project_dir = self.storage_dir / project_id
            delete_directory(project_dir)
            
            # 删除项目数据文件
            project_file = self._get_project_file_path(project_id)
            if project_file.exists():
                project_file.unlink()
            
            logger.info(f"删除项目成功: {project_id}")
            return True
        except Exception as e:
            logger.error(f"删除项目失败: {str(e)}")
            return False
    
    def upload_pdf(self, project_id: str, pdf_file) -> str:
        """上传PDF文件
        
        Args:
            project_id: 项目ID
            pdf_file: PDF文件对象
            
        Returns:
            PDF文件路径
        """
        # 检查项目是否存在
        project = self._load_project_data(project_id)
        if not project:
            raise Exception("项目不存在")
        
        try:
            # 生成安全的文件名
            safe_name = safe_filename(pdf_file.filename)
            pdf_filename = f"{safe_name}"
            pdf_path = self.storage_dir / project_id / pdf_filename
            
            # 保存文件
            if not save_upload_file(pdf_file, pdf_path):
                raise Exception("保存PDF文件失败")
            
            # 更新项目数据
            project.pdf_path = str(pdf_path)
            project.update_timestamp()
            
            # 保存更新后的数据
            if not self._save_project_data(project):
                raise Exception("保存项目数据失败")
            
            logger.info(f"上传PDF文件成功: {project_id} - {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            logger.error(f"上传PDF文件失败: {str(e)}")
            raise