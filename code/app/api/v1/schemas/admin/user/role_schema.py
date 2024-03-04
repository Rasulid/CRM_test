from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from api.v1.schemas.base_schema import ABaseModel, optional
from api.v1.schemas.admin.user.permission_schema import APermissionReadShortSchema


class ABaseRoleSchema(ABaseModel):
    title: str = Field(min_length=1)
    desc: Optional[str]
    organization_id: Optional[UUID]


class ARoleCreateSchema(ABaseRoleSchema):
    is_active: Optional[bool] = True


@optional
class ARoleUpdateSchema(ABaseRoleSchema):
    is_active: Optional[bool]


class ARoleReadSchema(ABaseRoleSchema):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    permissions: List[APermissionReadShortSchema]
    is_active: bool

    class Config:
        orm_mode = True


class ARoleReadSchemaForUserGet(ABaseRoleSchema):
    id: int
    permissions: List[APermissionReadShortSchema]

    class Config:
        orm_mode = True
