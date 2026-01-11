import json
from pathlib import Path
from typing import List, Optional
import logging

from app.models import Project, Image
from app.utils.file_utils import (
    generate_unique_id, 
    delete_directory,
    save_upload_file,
    safe_filename
)
from app.core.path_manager import PathManager

logger = logging.getLogger(__name__)


class ProjectService:
    """项目服务类"""
    
    def __init__(self, path_manager: Optional[PathManager] = None):
        """Initialize project service
        
        Args:
            path_manager: Path manager instance, if None uses global instance
        """
        self.path_manager = path_manager or PathManager()
    
    def _get_project_file_path(self, project_id: str) -> Path:
        """Get project data file path"""
        return self.path_manager.get_project_data_file(project_id)
    
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
        """Create new project
        
        Args:
            name: Project name
            
        Returns:
            Created project object
        """
        # Generate unique ID
        project_id = generate_unique_id()
        
        # Create project directory structure
        self.path_manager.ensure_project_structure(project_id)
        
        # Create project object
        project = Project(
            id=project_id,
            name=name
        )
        
        # Save project data
        if not self._save_project_data(project):
            raise Exception("Failed to save project data")
        
        logger.info(f"Project created successfully: {project_id}")
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
        """Get all projects list
        
        Returns:
            List of projects
        """
        projects = []
        
        # Iterate through all project files in data directory
        data_dir = self.path_manager.get_project_data_dir()
        for project_file in data_dir.glob("*.json"):
            project_id = project_file.stem
            project = self._load_project_data(project_id)
            if project:
                projects.append(project)
        
        # Sort by creation time in descending order
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects
    
    def update_project(self, project_id: str, name: str) -> Optional[Project]:
        """Update project name
        
        Args:
            project_id: Project ID
            name: New project name
            
        Returns:
            Updated project object, returns None if doesn't exist
        """
        project = self._load_project_data(project_id)
        if not project:
            return None
        
        # Update project name and timestamp
        project.name = name
        project.update_timestamp()
        
        # Save updated data
        if not self._save_project_data(project):
            raise Exception("Failed to save project data")
        
        logger.info(f"Project updated successfully: {project_id}")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project
        
        Args:
            project_id: Project ID
            
        Returns:
            Whether deletion was successful
        """
        # Check if project exists
        project = self._load_project_data(project_id)
        if not project:
            return False
        
        try:
            # Delete project directory
            project_dir = self.path_manager.get_project_dir(project_id)
            delete_directory(project_dir)
            
            # Delete project data file
            project_file = self._get_project_file_path(project_id)
            if project_file.exists():
                project_file.unlink()
            
            logger.info(f"Project deleted successfully: {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete project: {str(e)}")
            return False
    
    def upload_pdf(self, project_id: str, pdf_file) -> str:
        """Upload PDF file
        
        Args:
            project_id: Project ID
            pdf_file: PDF file object
            
        Returns:
            PDF file path
        """
        # Check if project exists
        project = self._load_project_data(project_id)
        if not project:
            raise Exception("Project doesn't exist")
        
        try:
            # Generate safe filename
            safe_name = safe_filename(pdf_file.filename)
            pdf_filename = f"{safe_name}"
            pdf_path = self.path_manager.get_project_dir(project_id) / pdf_filename
            
            # Save file
            if not save_upload_file(pdf_file, pdf_path):
                raise Exception("Failed to save PDF file")
            
            # Update project data
            project.pdf_path = str(pdf_path)
            project.update_timestamp()
            
            # Save updated data
            if not self._save_project_data(project):
                raise Exception("Failed to save project data")
            
            logger.info(f"PDF file uploaded successfully: {project_id} - {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            logger.error(f"Failed to upload PDF file: {str(e)}")
            raise