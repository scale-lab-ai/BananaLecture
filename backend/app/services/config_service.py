import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from app.config import config_manager

logger = logging.getLogger(__name__)


class ConfigService:
    """配置服务类"""
    
    def __init__(self):
        """初始化配置服务"""
        self.config_manager = config_manager
    
    def get_env_config(self) -> Dict[str, str]:
        """获取环境配置"""
        try:
            config = self.config_manager.get_config()
            return {
                "LLM_OPENAI_API_KEY": config.env.LLM_OPENAI_API_KEY,
                "LLM_OPENAI_BASE_URL": config.env.LLM_OPENAI_BASE_URL,
                "LLM_OPENAI_MODEL": config.env.LLM_OPENAI_MODEL,
                "MINIMAX_AUDIO_API_KEY": config.env.MINIMAX_AUDIO_API_KEY,
                "MINIMAX_AUDIO_GROUP_ID": config.env.MINIMAX_AUDIO_GROUP_ID,
                "MINIMAX_AUDIO_MODEL": config.env.MINIMAX_AUDIO_MODEL
            }
        except Exception as e:
            logger.error(f"获取环境配置失败: {str(e)}")
            raise
    
    def update_env_config(self, env_updates: Dict[str, str]) -> None:
        """更新环境配置"""
        try:
            # 更新配置
            self.config_manager.update_env_config(env_updates)
            
            # 保存到.env文件
            self.config_manager.save_env_config()
            
            logger.info("环境配置更新成功")
        except Exception as e:
            logger.error(f"更新环境配置失败: {str(e)}")
            raise
    
    def get_role_config(self) -> Dict[str, str]:
        """获取角色配置"""
        try:
            config = self.config_manager.get_config()
            return config.roles.mapping
        except Exception as e:
            logger.error(f"获取角色配置失败: {str(e)}")
            raise
    
    def update_role_config(self, role_mapping: Dict[str, str]) -> None:
        """更新角色配置"""
        try:
            # 更新角色配置
            self.config_manager.update_role_config(role_mapping)
            
            logger.info("角色配置更新成功")
        except Exception as e:
            logger.error(f"更新角色配置失败: {str(e)}")
            raise
    
    def get_default_role_config(self) -> Dict[str, str]:
        """获取默认角色配置"""
        return {
            "旁白": "Chinese (Mandarin)_Male_Announcer",
            "大雄": "Chinese (Mandarin)_ExplorativeGirl",
            "哆啦A梦": "Chinese (Mandarin)_Pure-hearted_Boy",
            "其他男声": "Chinese (Mandarin)_Pure-hearted_Boy",
            "其他女声": "Chinese (Mandarin)_ExplorativeGirl",
            "其他": "Chinese (Mandarin)_Radio_Host"
        }
    
    def reset_role_config_to_default(self) -> None:
        """重置角色配置为默认值"""
        try:
            default_config = self.get_default_role_config()
            self.update_role_config(default_config)
            
            logger.info("角色配置已重置为默认值")
        except Exception as e:
            logger.error(f"重置角色配置失败: {str(e)}")
            raise