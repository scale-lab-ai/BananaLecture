from typing import Optional
from pydantic import Field, ConfigDict

from .base import BaseIdentifiedModel
from .enums import TaskType, TaskStatus


class Task(BaseIdentifiedModel):
    model_config = ConfigDict(use_enum_values=True)
    
    type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="进度 (0.0-1.0)")
    current_step: int = Field(default=0, ge=0, description="当前步骤")
    total_steps: int = Field(default=0, ge=0, description="总步骤数")
    error_message: Optional[str] = Field(None, description="错误信息")