from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import Field
from pydantic.networks import AnyHttpUrl

from api.v1.schemas.admin.course.course_schema import ACourseShortReadSchemaOnlyI18n
from api.v1.schemas.base_schema import ABaseModel, optional, BaseListResponseSchema
from api.v1.schemas.admin.media.media_schema import AMediaReadSchema
from api.v1.schemas.admin.user.district_schema import ADistrictReadSchema
from api.v1.schemas.admin.user.region_schema import ARegionShortReadSchema


class AOrganizationTranslationSchema(ABaseModel):
    language_id: int
    title: str = Field(min_length=1)
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True


class ABaseOrganizationSchema(ABaseModel):
    director_id: Optional[UUID]
    legal_address_region_id: Optional[int]
    legal_address_district_id: Optional[int]
    identification_number: int
    bank_account: Optional[str]
    brand_name: Optional[str]
    domain_name: Optional[AnyHttpUrl]
    bank_mfo: Optional[str]
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False

    translations: List[AOrganizationTranslationSchema]


class AOrganizationCreateSchema(ABaseOrganizationSchema):
    pass


@optional
class AOrganizationUpdateSchema(ABaseOrganizationSchema):
    pass


class AOrganizationReadSchema(ABaseModel):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    logo: Optional[AMediaReadSchema]
    legal_address_region: Optional[ARegionShortReadSchema]
    legal_address_district: Optional[ADistrictReadSchema]
    identification_number: int
    bank_account: Optional[str]
    bank_mfo: Optional[str]
    is_active: Optional[bool] = Field(default=True)
    is_verified: Optional[bool] = Field(default=False)
    director_id: Optional[UUID]
    brand_name: Optional[str]
    domain_name: Optional[AnyHttpUrl]

    translations: List[AOrganizationTranslationSchema]
    allowed_courses: list[ACourseShortReadSchemaOnlyI18n]

    # promocode: List[APromocodeReadSchema]

    class Config:
        orm_mode = True


class AListResponseSchema(BaseListResponseSchema):
    results: List[AOrganizationReadSchema]


class AOrganizationReadSchemaWithCourses(AOrganizationReadSchema):
    allowed_courses: list[ACourseShortReadSchemaOnlyI18n]
