from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional

from app.models import (
    EnvConfigResponse, EnvConfigUpdateRequest,
    VoiceSettingResponse, VoiceSettingCreateRequest, VoiceSettingUpdateRequest,
    RoleListResponse, RoleCreateRequest, RoleRenameRequest,
    MessageResponse, VoiceGroupListResponse, VoiceGroupCreateRequest,
    VoiceGroupUpdateRequest, CurrentGroupResponse
)
from app.services.config_service import ConfigService

config_router = APIRouter(prefix="/api/config", tags=["config"])


# Dependency injection: Get configuration service
def get_config_service() -> ConfigService:
    return ConfigService()


@config_router.get("/env", response_model=EnvConfigResponse)
async def get_env_config(service: ConfigService = Depends(get_config_service)):
    """Get default environment configuration"""
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
        raise HTTPException(status_code=500, detail=f"Failed to get environment configuration: {str(e)}")


@config_router.put("/env", response_model=MessageResponse)
async def update_env_config(
    request: EnvConfigUpdateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Update environment configuration"""
    try:
        # Prepare update data
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

        # Update configuration
        service.update_env_config(env_updates)

        return MessageResponse(message="Environment configuration updated successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update environment configuration: {str(e)}")


@config_router.get("/roles", response_model=Dict[str, str])
async def get_role_config(service: ConfigService = Depends(get_config_service)):
    """Get role configuration"""
    try:
        return service.get_default_role_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get role configuration: {str(e)}")


# Voice settings endpoints
@config_router.get("/voices", response_model=VoiceSettingResponse)
async def get_voice_settings(service: ConfigService = Depends(get_config_service)):
    """Get all voice settings"""
    try:
        voice_settings = service.get_voice_settings()
        return VoiceSettingResponse(voices=voice_settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voice settings: {str(e)}")


@config_router.post("/voices", response_model=MessageResponse)
async def add_voice_setting(
    request: VoiceSettingCreateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Add a new voice setting"""
    try:
        voice_setting = {
            "voice_id": request.voice_id,
            "name": request.name,
            "gender": request.gender,
            "age_group": request.age_group,
            "language": request.language,
            "description": request.description,
            "example_url": request.example_url
        }
        service.add_voice_setting(voice_setting)
        return MessageResponse(message="Voice setting added successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add voice setting: {str(e)}")


@config_router.put("/voices/{voice_id}", response_model=MessageResponse)
async def update_voice_setting(
    voice_id: str,
    request: VoiceSettingUpdateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Update a voice setting"""
    try:
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.gender is not None:
            updates["gender"] = request.gender
        if request.age_group is not None:
            updates["age_group"] = request.age_group
        if request.language is not None:
            updates["language"] = request.language
        if request.description is not None:
            updates["description"] = request.description
        if request.example_url is not None:
            updates["example_url"] = request.example_url

        service.update_voice_setting(voice_id, updates)
        return MessageResponse(message="Voice setting updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update voice setting: {str(e)}")


@config_router.delete("/voices/{voice_id}", response_model=MessageResponse)
async def delete_voice_setting(
    voice_id: str,
    service: ConfigService = Depends(get_config_service)
):
    """Delete a voice setting"""
    try:
        service.delete_voice_setting(voice_id)
        return MessageResponse(message="Voice setting deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete voice setting: {str(e)}")


# Role management endpoints
@config_router.get("/roles/list", response_model=RoleListResponse)
async def get_role_list(service: ConfigService = Depends(get_config_service)):
    """Get list of roles with their associated voice IDs"""
    try:
        roles = service.get_role_list()
        return RoleListResponse(roles=roles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get role list: {str(e)}")


@config_router.post("/roles", response_model=MessageResponse)
async def add_role(
    request: RoleCreateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Add a new role"""
    try:
        service.add_role(request.name, request.voice_id)
        return MessageResponse(message="Role added successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add role: {str(e)}")


@config_router.delete("/roles/{role_name}", response_model=MessageResponse)
async def delete_role(
    role_name: str,
    service: ConfigService = Depends(get_config_service)
):
    """Delete a role"""
    try:
        service.delete_role(role_name)
        return MessageResponse(message="Role deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")


@config_router.put("/roles/{old_name}/rename", response_model=MessageResponse)
async def rename_role(
    old_name: str,
    request: RoleRenameRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Rename a role"""
    try:
        service.rename_role(old_name, request.new_name)
        return MessageResponse(message="Role renamed successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename role: {str(e)}")


@config_router.put("/roles/{role_name}/voice", response_model=MessageResponse)
async def update_role_voice(
    role_name: str,
    request: dict = Body(...),
    service: ConfigService = Depends(get_config_service)
):
    """Update the voice ID for a role"""
    try:
        voice_id = request.get('voice_id')
        if not voice_id:
            raise ValueError("voice_id is required")
        service.update_role_voice(role_name, voice_id)
        return MessageResponse(message="Role voice updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update role voice: {str(e)}")


# Voice group management endpoints
@config_router.get("/groups", response_model=VoiceGroupListResponse)
async def get_all_groups(service: ConfigService = Depends(get_config_service)):
    """Get all voice groups"""
    try:
        groups = service.get_all_groups()
        return VoiceGroupListResponse(groups=groups)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voice groups: {str(e)}")


@config_router.post("/groups", response_model=MessageResponse)
async def add_group(
    request: VoiceGroupCreateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Add a new voice group"""
    try:
        service.add_group(request.name, request.role)
        return MessageResponse(message="Voice group added successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add voice group: {str(e)}")


@config_router.put("/groups/{group_name}", response_model=MessageResponse)
async def update_group(
    group_name: str,
    request: VoiceGroupUpdateRequest,
    service: ConfigService = Depends(get_config_service)
):
    """Update a voice group"""
    try:
        service.update_group(group_name, request.name, request.role)
        return MessageResponse(message="Voice group updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update voice group: {str(e)}")


@config_router.delete("/groups/{group_name}", response_model=MessageResponse)
async def delete_group(
    group_name: str,
    service: ConfigService = Depends(get_config_service)
):
    """Delete a voice group"""
    try:
        service.delete_group(group_name)
        return MessageResponse(message="Voice group deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete voice group: {str(e)}")


@config_router.get("/current-group", response_model=CurrentGroupResponse)
async def get_current_group(service: ConfigService = Depends(get_config_service)):
    """Get current selected group"""
    try:
        current_group = service.get_current_group()
        return CurrentGroupResponse(current_group=current_group)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current group: {str(e)}")


@config_router.put("/current-group", response_model=MessageResponse)
async def set_current_group(
    request: dict = Body(...),
    service: ConfigService = Depends(get_config_service)
):
    """Set current selected group"""
    try:
        group_name = request.get('group_name')
        if not group_name:
            raise ValueError("group_name is required")
        service.set_current_group(group_name)
        return MessageResponse(message="Current group set successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set current group: {str(e)}")
