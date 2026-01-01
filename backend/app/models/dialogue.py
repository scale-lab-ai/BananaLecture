from typing import Optional
from pydantic import Field, ConfigDict

from .base import BaseIdentifiedModel
from .enums import DialogueRole, EmotionType, SpeechSpeed


class DialogueItem(BaseIdentifiedModel):
    model_config = ConfigDict(use_enum_values=True)
    
    role: DialogueRole = Field(..., description="角色")
    content: str = Field(..., min_length=1, description="对话内容")
    emotion: EmotionType = Field(default=EmotionType.AUTO, description="情感")
    speed: SpeechSpeed = Field(default=SpeechSpeed.NORMAL, description="语速")


class Script(BaseIdentifiedModel):
    model_config = ConfigDict(use_enum_values=True)
    
    page_number: int = Field(..., ge=1, description="页码")
    dialogues: list[DialogueItem] = Field(default_factory=list, description="对话列表")