from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema


class ADiscountTranslationSchema(ABaseModel):
    language_id: int
    title: str = Field(min_length=1)
    desc: Optional[str]
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True


class ABaseDiscountSchema(ABaseModel):
    percent: float
    start: date
    stop: date
    is_active: Optional[bool] = True
    is_archive: Optional[bool] = False

    translations: List[ADiscountTranslationSchema]


class ADiscountCreateSchema(ABaseDiscountSchema):
    pass


@optional
class ADiscountUpdateSchema(ABaseDiscountSchema):
    pass


class ADiscountReadSchema(ABaseDiscountSchema):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[ADiscountReadSchema]
