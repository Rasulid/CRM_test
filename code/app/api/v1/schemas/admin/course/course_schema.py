from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field, AnyHttpUrl

from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema
from api.v1.schemas.admin.course.category_schema import ACategoryReadSchema
from api.v1.schemas.admin.course.course_module_schema import ACourseModuleReadSchema
from api.v1.schemas.admin.course.tag_schema import ATagReadSchema
from api.v1.schemas.admin.media.media_schema import AMediaReadSchema
from api.v1.schemas.admin.payment.discount_schema import ADiscountReadSchema
from api.v1.schemas.admin.user.user_schema import AUserShortSchema
from api.v1.schemas.data_types import CourseStatusEnum, DifficultyLevelEnum


class ACourseTranslationSchema(ABaseModel):
    language_id: int
    title: str = Field(min_length=1)
    desc: Optional[str]
    sub_title: Optional[str]

    class Config:
        orm_mode = True


class ABaseCourseSchema(ABaseModel):
    is_active: Optional[bool] = Field(default=True)
    sort: Optional[int] = Field(ge=1)
    slug: Optional[str] = Field(default=None, min_length=1)
    price: float
    is_free: Optional[bool] = Field(default=False)
    status: CourseStatusEnum = Field(default=CourseStatusEnum.PUBLIC)
    is_verified: Optional[bool] = Field(default=False)
    is_for_child: Optional[bool] = Field(default=False)
    level: DifficultyLevelEnum = Field(default=DifficultyLevelEnum.BEGINNER)
    telegram_url: Optional[AnyHttpUrl]
    duration: Optional[int]
    translations: List[ACourseTranslationSchema]
    language_id: int


class ACourseCreateSchema(ABaseCourseSchema):
    course_old_id: Optional[int]
    banner_image_id: Optional[int]
    trailer_id: Optional[int]
    discount_id: Optional[UUID]
    organization_id: Optional[UUID]


@optional
class ACourseUpdateSchema(ABaseCourseSchema):
    discount_id: Optional[UUID]


class ACourseReadSchema(ABaseCourseSchema):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: AUserShortSchema
    mentors: List[AUserShortSchema]
    course_modules: List[ACourseModuleReadSchema]
    tag: List[ATagReadSchema]
    categories: List[ACategoryReadSchema]
    banner_image: Optional[AMediaReadSchema]
    banner_file: Optional[AMediaReadSchema]
    trailer: Optional[AMediaReadSchema]
    discount: Optional[ADiscountReadSchema]
    organization_id: Optional[UUID] = Field(None, exclude=True)

    class Config:
        orm_mode = True


class ACourseShortReadSchema(ABaseCourseSchema):
    id: int

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[ACourseShortReadSchema]


class ACourseCuratorsListResponseSchema(BaseListResponseSchema):
    results: List[AUserShortSchema]


class ACourseAccessListResponseSchema(BaseListResponseSchema):
    results: List[AUserShortSchema]


class ACourseShortReadSchemaOnlyI18n(ABaseModel):
    id: int
    translations: List[ACourseTranslationSchema]

    class Config:
        orm_mode = True
