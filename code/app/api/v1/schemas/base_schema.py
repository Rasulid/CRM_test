import datetime
import inspect
from typing import Optional, Any

import pytz

from core.babel_config import _
from pydantic import BaseModel, root_validator, validator

# https://github.com/pydantic/pydantic/issues/1223
# https://github.com/pydantic/pydantic/pull/3179
# Todo migrate to pydanticv2 partial
from core.config import settings

messages = {
    'type_error.float': _('Value is not a valid float'),
    'value_error.path.not_exists': _('Not a valid path: "{path}"'),
}


def optional(*fields):
    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
            if _cls.__fields__[field].default:
                _cls.__fields__[field].default = None
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)
    return dec


class _BaseModel(BaseModel):
    @root_validator
    def zero_to_none(cls, values) -> Any:
        return {k: v if v is not 0 else None for k, v in values.items()}

    @root_validator
    def empty_string_to_none(cls, values) -> Any:
        return {k: v if v != "" else None for k, v in values.items()}

    @validator("created_at", "updated_at", "deleted_at", "check_date", check_fields=False)
    def validate_datetime(cls, value, values, **kwargs):
        if value:
            if not isinstance(value, datetime.datetime):
                raise ValueError("Must be datetime")
            local_timezone = pytz.timezone(settings.TIMEZONE)
            if value.tzname() is None:
                return value.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        return value


class ABaseModel(_BaseModel):
    """
    Ushbu model faqat adminka uchun
    """

    # created_at: Optional[datetime.datetime]
    # updated_at: Optional[datetime.datetime]
    # deleted_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class IBaseModel(_BaseModel):
    """
    Ushbu model faqat site uchun
    """

    class Config:
        orm_mode = True


class BaseListResponseSchema(BaseModel):
    page_number: int
    page_size: int
    num_pages: int
    total_results: int
