from pydantic import BaseModel, Field
from datetime import datetime


class BaseTimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_timestamp(self):
        self.updated_at = datetime.now()


class BaseIdentifiedModel(BaseTimestampedModel):
    id: str = Field(..., description="唯一标识符")