from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional

from app.models import (
    EnvConfigResponse, EnvConfigUpdateRequest,
    RoleConfigResponse, RoleConfigUpdateRequest,
    MessageResponse
)
from app.services.config_service import ConfigService

config_router = APIRouter(prefix="/api/config", tags=["config"])


# 依赖注入：获取配置服务
def get_config_service() -> ConfigService:
    return ConfigService()


@config_router.get("/env", response_model=EnvConfigResponse)
async def get_env_config(service: ConfigService = Depends(get_config_service)):
    """获取默认环境配置"""
    try:
        env_config = service.get_env_config()
        
        return EnvConfigResponse(
            LLM_OPENAI_API_KEY=env_config.get("LLM_OPENAI_API_KEY", ""),
            LLM_OPENAI_BASE_URL=env_config.get("LLM_OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
            LLM_OPENAI_MODEL=env_config.get("LLM_OPENAI_MODEL", "qwen/qwen3-vl-235b-a22b-instruct"),
            MINIMAX_AUDIO_API_KEY=env_config.get("MINIMAX_AUDIO_API_KEY", ""),
            MINIMAX_AUDIO_GROUP_ID=env_config.get("MINIMAX_AUDIO_GROUP_ID", ""),
            MINIMAX_AUDIO_MODEL=env_config.get("MINIMAX_AUDIO_MODEL", "speech-2.6-hd")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取环境配置失败: {str(e)}")


@config_router.put("/env", response_model=MessageResponse)
async def update_env_config(
    request: EnvConfigUpdateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """更新环境配置"""
    try:
        # 准备更新数据
        env_updates = {}
        
        if request.LLM_OPENAI_API_KEY is not None:
            env_updates["LLM_OPENAI_API_KEY"] = request.LLM_OPENAI_API_KEY
        if request.LLM_OPENAI_BASE_URL is not None:
            env_updates["LLM_OPENAI_BASE_URL"] = request.LLM_OPENAI_BASE_URL
        if request.LLM_OPENAI_MODEL is not None:
            env_updates["LLM_OPENAI_MODEL"] = request.LLM_OPENAI_MODEL
        if request.MINIMAX_AUDIO_API_KEY is not None:
            env_updates["MINIMAX_AUDIO_API_KEY"] = request.MINIMAX_AUDIO_API_KEY
        if request.MINIMAX_AUDIO_GROUP_ID is not None:
            env_updates["MINIMAX_AUDIO_GROUP_ID"] = request.MINIMAX_AUDIO_GROUP_ID
        if request.MINIMAX_AUDIO_MODEL is not None:
            env_updates["MINIMAX_AUDIO_MODEL"] = request.MINIMAX_AUDIO_MODEL
        
        # 更新配置
        service.update_env_config(env_updates)
        
        return MessageResponse(message="环境配置更新成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新环境配置失败: {str(e)}")


@config_router.get("/roles", response_model=RoleConfigResponse)
async def get_role_config(service: ConfigService = Depends(get_config_service)):
    """获取角色配置"""
    try:
        # 获取默认角色配置，符合PRD要求
        default_config = service.get_default_role_config()
        
        return RoleConfigResponse(
            旁白=default_config["旁白"],
            大雄=default_config["大雄"],
            哆啦A梦=default_config["哆啦A梦"],
            其他男声=default_config["其他男声"],
            其他女声=default_config["其他女声"],
            其他=default_config["其他"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色配置失败: {str(e)}")


@config_router.put("/roles", response_model=MessageResponse)
async def update_role_config(
    request: RoleConfigUpdateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """更新角色配置"""
    try:
        # 将请求转换为字典格式
        role_mapping = {
            "旁白": request.旁白,
            "大雄": request.大雄,
            "哆啦A梦": request.哆啦A梦,
            "其他男声": request.其他男声,
            "其他女声": request.其他女声,
            "其他": request.其他
        }
        
        # 更新角色配置
        service.update_role_config(role_mapping)
        
        return MessageResponse(message="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新角色配置失败: {str(e)}")
