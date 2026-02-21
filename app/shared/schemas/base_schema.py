"""Base Pydantic schema."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


class BaseResponseSchema(BaseSchema):
    """Base response schema with audit fields."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
