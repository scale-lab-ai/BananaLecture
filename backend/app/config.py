import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class EnvConfig(BaseModel):
    """环境变量配置"""
    LLM_OPENAI_API_KEY: str = Field(default="", description="OpenAI API密钥")
    LLM_OPENAI_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenAI API基础URL")
    LLM_OPENAI_MODEL: str = Field(default="qwen/qwen3-vl-235b-a22b-instruct", description="OpenAI模型")
    MINIMAX_AUDIO_API_KEY: str = Field(default="", description="MiniMax音频API密钥")
    MINIMAX_AUDIO_GROUP_ID: str = Field(default="", description="MiniMax音频组ID")
    MINIMAX_AUDIO_MODEL: str = Field(default="speech-2.6-hd", description="MiniMax音频模型")


class RoleConfig(BaseModel):
    """角色配置"""
    mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "旁白": "Chinese (Mandarin)_Male_Announcer",
            "大雄": "Chinese (Mandarin)_ExplorativeGirl",
            "哆啦A梦": "Chinese (Mandarin)_Pure-hearted_Boy",
            "其他男声": "Chinese (Mandarin)_Pure-hearted_Boy",
            "其他女声": "Chinese (Mandarin)_ExplorativeGirl",
            "其他": "Chinese (Mandarin)_Radio_Host"
        },
        description="角色到声音的映射"
    )


class AppConfig(BaseModel):
    """应用配置"""
    env: EnvConfig = Field(default_factory=EnvConfig)
    roles: RoleConfig = Field(default_factory=RoleConfig)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._config: Optional[AppConfig] = None
        self._env_file_path = None
        self._config_file_path = None
        
    def _get_project_root(self) -> Path:
        """获取后端项目根目录"""
        return Path(__file__).parent.parent
    
    def _get_env_file_path(self) -> Path:
        """获取环境变量文件路径"""
        if self._env_file_path is None:
            project_root = self._get_project_root()
            env_file = project_root / ".env"
            env_example = project_root / ".env.example"
            
            # 优先使用.env，如果不存在则使用.env.example
            if env_file.exists():
                self._env_file_path = env_file
            else:
                self._env_file_path = env_example
                
        return self._env_file_path
    
    def _get_config_file_path(self) -> Path:
        """获取配置文件路径"""
        if self._config_file_path is None:
            project_root = self._get_project_root()
            self._config_file_path = project_root / "config.yaml"
            
        return self._config_file_path
    
    def load_env(self) -> None:
        """加载环境变量"""
        env_file = self._get_env_file_path()
        if env_file.exists():
            load_dotenv(env_file)
    
    def load_config(self) -> AppConfig:
        """加载配置"""
        if self._config is None:
            # 加载环境变量
            self.load_env()
            
            # 创建环境配置
            env_config = EnvConfig(
                LLM_OPENAI_API_KEY=os.getenv("LLM_OPENAI_API_KEY", ""),
                LLM_OPENAI_BASE_URL=os.getenv("LLM_OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
                LLM_OPENAI_MODEL=os.getenv("LLM_OPENAI_MODEL", "qwen/qwen3-vl-235b-a22b-instruct"),
                MINIMAX_AUDIO_API_KEY=os.getenv("MINIMAX_AUDIO_API_KEY", ""),
                MINIMAX_AUDIO_GROUP_ID=os.getenv("MINIMAX_AUDIO_GROUP_ID", ""),
                MINIMAX_AUDIO_MODEL=os.getenv("MINIMAX_AUDIO_MODEL", "speech-2.6-hd")
            )
            
            # 加载角色配置
            config_file = self._get_config_file_path()
            role_mapping = {}
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    if config_data and 'role' in config_data:
                        role_mapping = config_data['role']
            
            role_config = RoleConfig(mapping=role_mapping)
            
            # 创建应用配置
            self._config = AppConfig(
                env=env_config,
                roles=role_config
            )
            
        return self._config
    
    def get_config(self) -> AppConfig:
        """获取配置"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def update_env_config(self, env_updates: Dict[str, str]) -> None:
        """更新环境配置"""
        config = self.get_config()
        
        for key, value in env_updates.items():
            if hasattr(config.env, key):
                setattr(config.env, key, value)
                os.environ[key] = value
    
    def update_role_config(self, role_updates: Dict[str, str]) -> None:
        """更新角色配置"""
        config = self.get_config()
        config.roles.mapping.update(role_updates)
        
        # 保存到配置文件
        config_file = self._get_config_file_path()
        config_data = {'role': config.roles.mapping}
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def save_env_config(self) -> None:
        """保存环境配置到.env文件"""
        env_file = self._get_env_file_path()
        config = self.get_config()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f'LLM_OPENAI_API_KEY="{config.env.LLM_OPENAI_API_KEY}"\n')
            f.write(f'LLM_OPENAI_BASE_URL="{config.env.LLM_OPENAI_BASE_URL}"\n')
            f.write(f'LLM_OPENAI_MODEL="{config.env.LLM_OPENAI_MODEL}"\n')
            f.write(f'MINIMAX_AUDIO_API_KEY="{config.env.MINIMAX_AUDIO_API_KEY}"\n')
            f.write(f'MINIMAX_AUDIO_GROUP_ID="{config.env.MINIMAX_AUDIO_GROUP_ID}"\n')
            f.write(f'MINIMAX_AUDIO_MODEL="{config.env.MINIMAX_AUDIO_MODEL}"\n')


# 全局配置管理器实例
config_manager = ConfigManager()