import json
from datetime import datetime
from typing import Optional, List, Union

from fastapi import UploadFile

from api.v1.schemas.admin.media.media_schema import AMediaReadSchema
from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema
from pydantic import Field


class ACategoryTranslationSchema(ABaseModel):
    language_id: int
    title: str = Field(min_length=1)
    desc: Optional[str]

    class Config:
        orm_mode = True


class ABaseCategorySchema(ABaseModel):
    is_active: Optional[bool]
    sort: Optional[int] = Field(ge=1)
    slug: str = Field(default=None, min_length=1)
    topic_id: int
    # logo_id: int
    translations: List[ACategoryTranslationSchema]


class ACategoryCreateSchema(ABaseCategorySchema):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


@optional
class ACategoryUpdateSchema(ABaseCategorySchema):
    # logo: Optional[AMediaReadSchema]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ACategoryReadSchema(ABaseCategorySchema):
    id: int
    logo: Optional[AMediaReadSchema]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[ACategoryReadSchema]
