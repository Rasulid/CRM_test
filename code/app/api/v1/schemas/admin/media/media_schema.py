from datetime import datetime
from typing import Optional
from uuid import UUID
from api.v1.schemas.base_schema import ABaseModel


class ABaseMediaSchema(ABaseModel):
    filename: str
    path: str
    size: int
    file_format: str
    created_by_id: Optional[UUID]


class AMediaCreateSchema(ABaseMediaSchema):
    pass


class AMediaReadSchema(ABaseMediaSchema):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AMediaShortReadSchema(ABaseModel):
    filename: str
    path: str
