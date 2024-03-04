from datetime import datetime
from typing import Optional, List
from uuid import UUID

from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema
from pydantic import Field

from api.v1.schemas.data_types import DifficultyLevelEnum


class ACourseModuleTranslationSchema(ABaseModel):
    language_id: int
    title: str = Field(min_length=1)
    desc: Optional[str]
    content: Optional[str]

    class Config:
        orm_mode = True


class ABaseCourseModuleSchema(ABaseModel):
    is_active: Optional[bool] = Field(default=True)
    sort: Optional[int] = Field(ge=1)
    slug: Optional[str] = Field(default=None, min_length=1)
    course_id: int
    price: Optional[float]
    is_free: Optional[bool] = Field(default=False)
    is_final: Optional[bool] = Field(default=False)
    level: DifficultyLevelEnum = Field(default=DifficultyLevelEnum.BEGINNER)
    discount_id: Optional[UUID]

    translations: List[ACourseModuleTranslationSchema]


class ACourseModuleCreateSchema(ABaseCourseModuleSchema):
    pass


@optional
class ACourseModuleUpdateSchema(ABaseCourseModuleSchema):
    pass


class ACourseModuleReadSchema(ABaseCourseModuleSchema):
    id: int
    created_at: datetime
    discount_id: Optional[int]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[ACourseModuleReadSchema]


class ACourseModuleShortReadSchemaForUserPurchase(ABaseModel):
    id: int
    translations: List[ACourseModuleTranslationSchema]

    class Config:
        orm_mode = True


class ACourseModuleShortReadSchemaI18nCourseId(ABaseModel):
    id: int
    course_id: int
    translations: List[ACourseModuleTranslationSchema]

    class Config:
        orm_mode = True
