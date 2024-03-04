from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema


class ABasePermissionSchema(ABaseModel):
    title: str = Field(min_length=1)
    desc: Optional[str]
    is_active: Optional[bool] = True


class APermissionCreateSchema(ABasePermissionSchema):
    pass


@optional
class APermissionUpdateSchema(ABasePermissionSchema):
    pass


class APermissionReadSchema(ABasePermissionSchema):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class APermissionReadShortSchema(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[APermissionReadSchema]
