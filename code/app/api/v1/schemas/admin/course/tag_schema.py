from datetime import datetime
from typing import List, Optional

from pydantic import Field

from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema


class ABaseTagSchema(ABaseModel):
    title: str = Field(min_length=1)
    slug: str = Field(default=None, min_length=1)


class ATagCreateSchema(ABaseTagSchema):
    pass


@optional
class ATagUpdateSchema(ABaseTagSchema):
    pass


class ATagReadSchema(ABaseTagSchema):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    slug: str

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[ATagReadSchema]
