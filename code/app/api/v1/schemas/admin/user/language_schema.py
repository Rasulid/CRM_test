import json
from datetime import datetime
from typing import Optional

from pydantic import Field

from api.v1.schemas.admin.media.media_schema import AMediaShortReadSchema
from api.v1.schemas.base_schema import ABaseModel, optional


class ALanguageCreateSchema(ABaseModel):
    title: dict = {"en": "Uzbek"}
    code: str = 'uz'
    is_active: Optional[bool] = Field(default=True)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    # @validator('title', pre=True)
    # def validate_title(cls, v, values, **kwargs):
    #     if isinstance(v, dict):
    #         return json.dumps(v, ensure_ascii=False)
    #     else:
    #         return v


@optional
class ALanguageUpdateSchema(ALanguageCreateSchema):
    is_active: Optional[bool]

    # @validator('title', pre=True)
    # def validate_title(cls, v, values, **kwargs):
    #     print(33, v)
    #     return v
    # if isinstance(v, dict):
    #     return json.dumps(v, ensure_ascii=False)
    # else:
    #     return v


class ALanguageReadSchema(ABaseModel):
    id: int
    title: dict
    code: str
    is_active: bool
    flag: AMediaShortReadSchema
    created_at: datetime
    updated_at: Optional[datetime]

    # @validator('title', pre=True)
    # def validate_title(cls, v, values, **kwargs):
    #     print(49, v)
    #     if isinstance(v, str):
    #         return json.loads(v)
    #     else:
    #         return v

    class Config:
        orm_mode = True

# ALTER table language ALTER column title TYPE json USING title::json
