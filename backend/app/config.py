import os
import json
import shutil
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.core.path_manager import path_manager


class EnvConfig(BaseModel):
    """Environment configuration"""
    LLM_OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    LLM_OPENAI_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenAI API base URL")
    LLM_OPENAI_MODEL: str = Field(default="qwen/qwen3-vl-235b-a22b-instruct", description="OpenAI model")
    MINIMAX_AUDIO_API_KEY: str = Field(default="", description="MiniMax audio API key")
    MINIMAX_AUDIO_GROUP_ID: str = Field(default="", description="MiniMax audio group ID")
    MINIMAX_AUDIO_MODEL: str = Field(default="speech-2.6-hd", description="MiniMax audio model")


class AppConfig(BaseModel):
    """Application configuration"""
    env: EnvConfig = Field(default_factory=EnvConfig)
    current_group: str = Field(default="default", description="current voice group")


class ConfigManager:
    """Configuration manager"""
    
    def __init__(self):
        """Initialize configuration manager"""
        self._config: Optional[AppConfig] = None
        self._env_file_path = None
        self._config_file_path = None
        
    def load_env(self) -> None:
        """Load environment variables"""
        env_file = path_manager.get_env_file_path()
        if env_file.exists():
            load_dotenv(env_file)
    
    def _copy_default_configs_to_storage(self) -> None:
        """Copy default configuration files to storage directory"""
        storage_config_dir = path_manager.get_storage_config_dir()
        
        # Copy audio_group.json if not exists
        default_audio_group = path_manager.get_config_dir() / "audio_group.json"
        storage_audio_group = path_manager.get_storage_audio_group_path()
        if not storage_audio_group.exists() and default_audio_group.exists():
            shutil.copy(default_audio_group, storage_audio_group)
        
        # Copy audio_setting.json if not exists
        default_audio_setting = path_manager.get_config_dir() / "audio_setting.json"
        storage_audio_setting = path_manager.get_storage_audio_setting_path()
        if not storage_audio_setting.exists() and default_audio_setting.exists():
            shutil.copy(default_audio_setting, storage_audio_setting)
        
        # Create default config.json if not exists
        storage_config_json = path_manager.get_storage_config_json_path()
        if not storage_config_json.exists():
            default_config = {
                "current_group": "default",
            }
            with open(storage_config_json, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def load_config(self) -> AppConfig:
        """Load configuration"""
        if self._config is None:
            # Copy default configs to storage if not exists
            self._copy_default_configs_to_storage()
            
            # Load environment variables
            self.load_env()
            
            # Create environment configuration
            env_config = EnvConfig(
                LLM_OPENAI_API_KEY=os.getenv("LLM_OPENAI_API_KEY", ""),
                LLM_OPENAI_BASE_URL=os.getenv("LLM_OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
                LLM_OPENAI_MODEL=os.getenv("LLM_OPENAI_MODEL", "qwen/qwen3-vl-235b-a22b-instruct"),
                MINIMAX_AUDIO_API_KEY=os.getenv("MINIMAX_AUDIO_API_KEY", ""),
                MINIMAX_AUDIO_GROUP_ID=os.getenv("MINIMAX_AUDIO_GROUP_ID", ""),
                MINIMAX_AUDIO_MODEL=os.getenv("MINIMAX_AUDIO_MODEL", "speech-2.6-hd")
            )
            
            # Create application configuration
            self._config = AppConfig(
                env=env_config,
                current_group=self.get_current_group()
            )
            
        return self._config
    
    def get_config(self) -> AppConfig:
        """Get configuration"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def update_env_config(self, env_updates: Dict[str, str]) -> None:
        """Update environment configuration"""
        config = self.get_config()
        
        for key, value in env_updates.items():
            if hasattr(config.env, key):
                setattr(config.env, key, value)
                os.environ[key] = value
    
    def save_env_config(self) -> None:
        """Save environment configuration to .env file"""
        env_file = path_manager.get_env_file_path()
        config = self.get_config()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f'LLM_OPENAI_API_KEY="{config.env.LLM_OPENAI_API_KEY}"\n')
            f.write(f'LLM_OPENAI_BASE_URL="{config.env.LLM_OPENAI_BASE_URL}"\n')
            f.write(f'LLM_OPENAI_MODEL="{config.env.LLM_OPENAI_MODEL}"\n')
            f.write(f'MINIMAX_AUDIO_API_KEY="{config.env.MINIMAX_AUDIO_API_KEY}"\n')
            f.write(f'MINIMAX_AUDIO_GROUP_ID="{config.env.MINIMAX_AUDIO_GROUP_ID}"\n')
            f.write(f'MINIMAX_AUDIO_MODEL="{config.env.MINIMAX_AUDIO_MODEL}"\n')
    
    def get_current_group(self) -> str:
        """Get current selected group"""
        storage_config_json = path_manager.get_storage_config_json_path()
        
        if storage_config_json.exists():
            with open(storage_config_json, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                return config_data.get('current_group', 'default')
        
        return 'default'
    
    def get_current_role_voice(self) -> Dict[str, str]:
        """Get all voice groups"""
        storage_audio_group = path_manager.get_storage_audio_group_path()
        with open(storage_audio_group, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        current_group = self.get_current_group()
        for group in config_data:
            if group['name'] == current_group:
                return group['role']
        return {}
            

# Global configuration manager instance
config_manager = ConfigManager()
