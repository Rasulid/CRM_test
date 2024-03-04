from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, root_validator

from api.v1.exceptions import CustomValidationError
from api.v1.schemas.admin.media.media_schema import AMediaReadSchema
from api.v1.schemas.admin.user.permission_schema import APermissionReadShortSchema
from api.v1.schemas.admin.user.role_schema import ARoleReadSchemaForUserGet
from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema
from api.v1.schemas.data_types import PhoneStr, GenderStatusEnum, PasswordStr


class AUserTranslationSchema(ABaseModel):
    language_id: int
    first_name: str
    last_name: Optional[str]
    street: Optional[str]

    class Config:
        orm_mode = True


class ABaseUserSchema(ABaseModel):
    birthday: Optional[date]
    region_id: Optional[int] = None
    district_id: Optional[int] = None
    gender: GenderStatusEnum = Field(default=GenderStatusEnum.MALE)
    phone: Optional[PhoneStr]
    email: Optional[EmailStr]
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    hashed_password: Optional[str]
    translations: List[AUserTranslationSchema]

    class Config:
        arbitrary_types_allowed = True


class AUserCreateSchema(ABaseUserSchema):
    class Config:
        orm_mode = True

    organization_id: Optional[UUID]

    # confirm_password: str

    @root_validator
    def email_or_phone_check(cls, values) -> dict:
        if not (values['email'] or values['phone']):
            raise CustomValidationError("Email or phone required")
        return values


class AUserCreateForTransferSchema(ABaseUserSchema):
    email: Optional[str]
    user_id: Optional[int]

    class Config:
        orm_mode = True

    organization_id: Optional[UUID]


class AUserCreateWithoutOrganizationSchema(ABaseUserSchema):
    organization_id: Optional[UUID]


@optional
class AUserUpdateSchema(ABaseUserSchema):
    organization_id: Optional[UUID]


class AUserReadSchema(ABaseUserSchema):
    id: UUID
    email: Optional[EmailStr]
    created_at: datetime
    updated_at: Optional[datetime]
    image: Optional[AMediaReadSchema]
    roles: List[ARoleReadSchemaForUserGet]
    self_permissions: Optional[List[APermissionReadShortSchema]]
    # organization_id: Optional[UUID] = Field(None, exclude=True)
    organization_id: Optional[UUID]

    class Config:
        orm_mode = True


class AUserShortSchema(BaseModel):
    id: UUID
    email: Optional[EmailStr]
    phone: Optional[PhoneStr]
    translations: List[AUserTranslationSchema]

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[AUserReadSchema]


class AListResponseShortSchema(BaseListResponseSchema):
    results: List[AUserShortSchema]


class ANotificationReadSchema(ABaseModel):
    sender: AUserShortSchema
    content: str
    is_read: bool

    class Config:
        orm_mode = True


class AUserMeSchema(BaseModel):
    id: UUID
    email: EmailStr
    permissions: list
    notifications: Optional[list[ANotificationReadSchema]]


class AUserChangePasswordSchema(BaseModel):
    current_password: PasswordStr
    new_password: PasswordStr


class ACourseStudentListResponseSchema(BaseListResponseSchema):
    results: List[AUserShortSchema]
