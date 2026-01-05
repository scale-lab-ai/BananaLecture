from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EnvConfigResponse(BaseModel):
    """环境配置响应模型"""
    LLM_OPENAI_API_KEY: str = Field(default="", description="OpenAI API密钥")
    LLM_OPENAI_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenAI API基础URL")
    LLM_OPENAI_MODEL: str = Field(default="qwen/qwen3-vl-235b-a22b-instruct", description="OpenAI模型")
    MINIMAX_AUDIO_API_KEY: str = Field(default="", description="MiniMax音频API密钥")
    MINIMAX_AUDIO_GROUP_ID: str = Field(default="", description="MiniMax音频组ID")
    MINIMAX_AUDIO_MODEL: str = Field(default="speech-2.6-hd", description="MiniMax音频模型")


class EnvConfigUpdateRequest(BaseModel):
    """环境配置更新请求模型"""
    LLM_OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API密钥")
    LLM_OPENAI_BASE_URL: Optional[str] = Field(default=None, description="OpenAI API基础URL")
    LLM_OPENAI_MODEL: Optional[str] = Field(default=None, description="OpenAI模型")
    MINIMAX_AUDIO_API_KEY: Optional[str] = Field(default=None, description="MiniMax音频API密钥")
    MINIMAX_AUDIO_GROUP_ID: Optional[str] = Field(default=None, description="MiniMax音频组ID")
    MINIMAX_AUDIO_MODEL: Optional[str] = Field(default=None, description="MiniMax音频模型")


class RoleConfigResponse(BaseModel):
    """角色配置响应模型"""
    # 硬编码的角色映射，符合PRD要求
    旁白: str = Field(default="Chinese (Mandarin)_Male_Announcer", description="旁白角色声音")
    大雄: str = Field(default="Chinese (Mandarin)_ExplorativeGirl", description="大雄角色声音")
    哆啦A梦: str = Field(default="Chinese (Mandarin)_Pure-hearted_Boy", description="哆啦A梦角色声音")
    其他男声: str = Field(default="Chinese (Mandarin)_Pure-hearted_Boy", description="其他男声角色声音")
    其他女声: str = Field(default="Chinese (Mandarin)_ExplorativeGirl", description="其他女声角色声音")
    其他: str = Field(default="Chinese (Mandarin)_Radio_Host", description="其他角色声音")


class RoleConfigUpdateRequest(BaseModel):
    """角色配置更新请求模型"""
    # 硬编码的角色映射，符合PRD要求
    旁白: str = Field(default="Chinese (Mandarin)_Male_Announcer", description="旁白角色声音")
    大雄: str = Field(default="Chinese (Mandarin)_ExplorativeGirl", description="大雄角色声音")
    哆啦A梦: str = Field(default="Chinese (Mandarin)_Pure-hearted_Boy", description="哆啦A梦角色声音")
    其他男声: str = Field(default="Chinese (Mandarin)_Pure-hearted_Boy", description="其他男声角色声音")
    其他女声: str = Field(default="Chinese (Mandarin)_ExplorativeGirl", description="其他女声角色声音")
    其他: str = Field(default="Chinese (Mandarin)_Radio_Host", description="其他角色声音")