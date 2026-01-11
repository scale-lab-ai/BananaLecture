from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class EnvConfigResponse(BaseModel):
    """Environment configuration response model"""
    LLM_OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    LLM_OPENAI_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenAI API base URL")
    LLM_OPENAI_MODEL: str = Field(default="qwen/qwen3-vl-235b-a22b-instruct", description="OpenAI model")
    MINIMAX_AUDIO_API_KEY: str = Field(default="", description="MiniMax audio API key")
    MINIMAX_AUDIO_GROUP_ID: str = Field(default="", description="MiniMax audio group ID")
    MINIMAX_AUDIO_MODEL: str = Field(default="speech-2.6-hd", description="MiniMax audio model")


class EnvConfigUpdateRequest(BaseModel):
    """Environment configuration update request model"""
    LLM_OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    LLM_OPENAI_BASE_URL: Optional[str] = Field(default=None, description="OpenAI API base URL")
    LLM_OPENAI_MODEL: Optional[str] = Field(default=None, description="OpenAI model")
    MINIMAX_AUDIO_API_KEY: Optional[str] = Field(default=None, description="MiniMax audio API key")
    MINIMAX_AUDIO_GROUP_ID: Optional[str] = Field(default=None, description="MiniMax audio group ID")
    MINIMAX_AUDIO_MODEL: Optional[str] = Field(default=None, description="MiniMax audio model")

class VoiceSetting(BaseModel):
    """Voice setting model"""
    voice_id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Voice name")
    gender: str = Field(..., description="Gender: 男/女")
    age_group: str = Field(..., description="Age group: 少年/青年/中年/老年")
    language: str = Field(..., description="Language: 中文/英文")
    description: str = Field(default="", description="Voice description")
    example_url: str = Field(default="", description="Example audio URL")


class VoiceSettingResponse(BaseModel):
    """Voice setting response model"""
    voices: List[VoiceSetting] = Field(default_factory=list, description="List of voice settings")


class VoiceSettingCreateRequest(BaseModel):
    """Voice setting create request model"""
    voice_id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Voice name")
    gender: str = Field(..., description="Gender: 男/女")
    age_group: str = Field(..., description="Age group: 少年/青年/中年/老年")
    language: str = Field(..., description="Language: 中文/英文")
    description: str = Field(default="", description="Voice description")
    example_url: str = Field(default="", description="Example audio URL")


class VoiceSettingUpdateRequest(BaseModel):
    """Voice setting update request model"""
    name: Optional[str] = Field(default=None, description="Voice name")
    gender: Optional[str] = Field(default=None, description="Gender: 男/女")
    age_group: Optional[str] = Field(default=None, description="Age group: 少年/青年/中年/老年")
    language: Optional[str] = Field(default=None, description="Language: 中文/英文")
    description: Optional[str] = Field(default=None, description="Voice description")
    example_url: Optional[str] = Field(default=None, description="Example audio URL")


class RoleItem(BaseModel):
    """Role item model"""
    name: str = Field(..., description="Role name")
    voice_id: str = Field(..., description="Associated voice ID")


class RoleListResponse(BaseModel):
    """Role list response model"""
    roles: List[RoleItem] = Field(default_factory=list, description="List of roles")


class RoleCreateRequest(BaseModel):
    """Role create request model"""
    name: str = Field(..., description="Role name")
    voice_id: str = Field(default="", description="Associated voice ID")


class RoleRenameRequest(BaseModel):
    """Role rename request model"""
    new_name: str = Field(..., description="New role name")


class MessageResponse(BaseModel):
    """Generic message response model"""
    message: str = Field(..., description="Response message")


class VoiceGroup(BaseModel):
    """Voice group model"""
    name: str = Field(..., description="Group name")
    role: Dict[str, str] = Field(default_factory=dict, description="Role to voice ID mapping")


class VoiceGroupListResponse(BaseModel):
    """Voice group list response model"""
    groups: List[VoiceGroup] = Field(default_factory=list, description="List of voice groups")


class VoiceGroupCreateRequest(BaseModel):
    """Voice group create request model"""
    name: str = Field(..., description="Group name")
    role: Dict[str, str] = Field(default_factory=dict, description="Role to voice ID mapping")


class VoiceGroupUpdateRequest(BaseModel):
    """Voice group update request model"""
    name: Optional[str] = Field(default=None, description="New group name")
    role: Optional[Dict[str, str]] = Field(default=None, description="Role to voice ID mapping")


class ConfigJson(BaseModel):
    """Config JSON model"""
    current_group: str = Field(default="default", description="Current selected group name")
    role_mapping: Dict[str, str] = Field(default_factory=dict, description="Current role to voice ID mapping")


class CurrentGroupResponse(BaseModel):
    """Current group response model"""
    current_group: str = Field(..., description="Current selected group name")