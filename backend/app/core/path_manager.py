import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PathManager:
    """Unified path manager for backend application"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize path manager
        
        Args:
            base_dir: Base directory for the application. If None, uses current working directory
        """
        if base_dir is None:
            self._base_dir = Path(__file__).parent.parent.parent.parent  # app/
        else:
            self._base_dir = Path(base_dir)
        
        self._backend_root = self._base_dir / "backend"
        
        # Cache paths
        self._storage_dir = None
        self._projects_dir = None
        self._tasks_dir = None
        self._assets_dir = None
        self._config_dir = None
        self._project_data_dir = None
        self._storage_config_dir = None
    
    def get_project_root(self) -> Path:
        """Get backend project root directory"""
        return self._backend_root
    
    def get_storage_dir(self) -> Path:
        """Get storage base directory"""
        if self._storage_dir is None:
            self._storage_dir = self._base_dir / "storage"
            self._storage_dir.mkdir(parents=True, exist_ok=True)
        return self._storage_dir
    
    def get_projects_dir(self) -> Path:
        """Get projects directory"""
        if self._projects_dir is None:
            self._projects_dir = self.get_storage_dir() / "projects"
            self._projects_dir.mkdir(parents=True, exist_ok=True)
        return self._projects_dir
    
    def get_tasks_dir(self) -> Path:
        """Get tasks directory"""
        if self._tasks_dir is None:
            self._tasks_dir = self.get_storage_dir() / "tasks"
            self._tasks_dir.mkdir(parents=True, exist_ok=True)
        return self._tasks_dir
    
    def get_assets_dir(self) -> Path:
        """Get assets directory"""
        if self._assets_dir is None:
            self._assets_dir = self._backend_root / "assets"
        return self._assets_dir
    
    def get_config_dir(self) -> Path:
        """Get config directory"""
        if self._config_dir is None:
            self._config_dir = self._backend_root / "app" / "config"
        return self._config_dir
    
    def get_project_data_dir(self) -> Path:
        """Get project data directory (for storing project metadata)"""
        if self._project_data_dir is None:
            self._project_data_dir = self.get_projects_dir() / "data"
            self._project_data_dir.mkdir(parents=True, exist_ok=True)
        return self._project_data_dir
    
    def get_project_dir(self, project_id: str) -> Path:
        """Get project directory by project ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project directory path
        """
        return self.get_projects_dir() / project_id
    
    def get_project_images_dir(self, project_id: str) -> Path:
        """Get project images directory
        
        Args:
            project_id: Project ID
            
        Returns:
            Images directory path
        """
        return self.get_project_dir(project_id) / "images"
    
    def get_project_scripts_dir(self, project_id: str) -> Path:
        """Get project scripts directory
        
        Args:
            project_id: Project ID
            
        Returns:
            Scripts directory path
        """
        return self.get_project_dir(project_id) / "scripts"
    
    def get_project_audio_dir(self, project_id: str) -> Path:
        """Get project audio directory
        
        Args:
            project_id: Project ID
            
        Returns:
            Audio directory path
        """
        return self.get_project_dir(project_id) / "audio"
    
    def get_project_page_audio_dir(self, project_id: str, page_number: int) -> Path:
        """Get project page audio directory
        
        Args:
            project_id: Project ID
            page_number: Page number
            
        Returns:
            Page audio directory path
        """
        page_path = self.get_project_audio_dir(project_id) / f"page_{page_number:03d}"
        page_path.mkdir(parents=True, exist_ok=True)
        return page_path
    
    def get_project_script_file(self, project_id: str, page_number: int) -> Path:
        """Get project script file path
        
        Args:
            project_id: Project ID
            page_number: Page number
            
        Returns:
            Script file path
        """
        return self.get_project_scripts_dir(project_id) / f"script_{page_number:03d}.json"
    
    def get_project_page_audio_file(self, project_id: str, page_number: int) -> Path:
        """Get project page audio file path
        
        Args:
            project_id: Project ID
            page_number: Page number
            
        Returns:
            Page audio file path
        """
        return self.get_project_audio_dir(project_id) / f"page_{page_number:03d}.mp3"
    
    def get_project_dialogue_audio_file(self, project_id: str, page_number: int, dialogue_id: str) -> Path:
        """Get project dialogue audio file path
        
        Args:
            project_id: Project ID
            page_number: Page number
            dialogue_id: Dialogue ID
            
        Returns:
            Dialogue audio file path
        """
        return self.get_project_page_audio_dir(project_id, page_number) / f"{dialogue_id}.mp3"
    
    def get_project_image_file(self, project_id: str, page_number: int, extension: str = "png") -> Path:
        """Get project image file path
        
        Args:
            project_id: Project ID
            page_number: Page number
            extension: Image file extension (default: png)
            
        Returns:
            Image file path
        """
        return self.get_project_images_dir(project_id) / f"page_{page_number:03d}.{extension}"
    
    def get_project_data_file(self, project_id: str) -> Path:
        """Get project data file path
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data file path
        """
        return self.get_project_data_dir() / f"{project_id}.json"
    
    def get_task_file(self, task_id: str) -> Path:
        """Get task file path
        
        Args:
            task_id: Task ID
            
        Returns:
            Task file path
        """
        return self.get_tasks_dir() / f"{task_id}.json"
    
    def get_env_file_path(self) -> Path:
        """Get .env file path
        
        Returns:
            .env file path (or .env.example if .env doesn't exist)
        """
        env_file = self._base_dir / ".env"
        env_example = self._base_dir / ".env.example"
        
        if env_file.exists():
            return env_file
        else:
            return env_example
    
    def get_config_file_path(self) -> Path:
        """Get config.yaml file path
        
        Returns:
            config.yaml file path
        """
        return self._base_dir / "config.yaml"
    
    def get_audio_setting_path(self) -> Path:
        """Get audio_setting.json file path
        
        Returns:
            audio_setting.json file path
        """
        return self.get_config_dir() / "audio_setting.json"
    
    def get_cues_audio_path(self) -> Path:
        """Get cues.mp3 file path
        
        Returns:
            cues.mp3 file path
        """
        return self.get_assets_dir() / "cues.mp3"
    
    def get_gadgets_audio_path(self) -> Path:
        """Get gadgets.mp3 file path
        
        Returns:
            gadgets.mp3 file path
        """
        return self.get_assets_dir() / "gadgets.mp3"
    
    def ensure_project_structure(self, project_id: str) -> None:
        """Ensure all project directories exist
        
        Args:
            project_id: Project ID
            
        Returns:
            None
        """
        # Create project directory structure
        self.get_project_dir(project_id).mkdir(parents=True, exist_ok=True)
        self.get_project_images_dir(project_id).mkdir(parents=True, exist_ok=True)
        self.get_project_scripts_dir(project_id).mkdir(parents=True, exist_ok=True)
        self.get_project_audio_dir(project_id).mkdir(parents=True, exist_ok=True)

    def get_storage_config_dir(self) -> Path:
        """Get storage config directory
        
        Returns:
            Storage config directory path
        """
        if self._storage_config_dir is None:
            self._storage_config_dir = self.get_storage_dir() / "config"
            self._storage_config_dir.mkdir(parents=True, exist_ok=True)
        return self._storage_config_dir

    def get_storage_audio_group_path(self) -> Path:
        """Get storage audio_group.json file path
        
        Returns:
            audio_group.json file path in storage
        """
        return self.get_storage_config_dir() / "audio_group.json"

    def get_storage_audio_setting_path(self) -> Path:
        """Get storage audio_setting.json file path
        
        Returns:
            audio_setting.json file path in storage
        """
        return self.get_storage_config_dir() / "audio_setting.json"

    def get_storage_config_json_path(self) -> Path:
        """Get storage config.json file path
        
        Returns:
            config.json file path in storage (contains current group and role mapping)
        """
        return self.get_storage_config_dir() / "config.json"


# Global path manager instance
path_manager = PathManager()
