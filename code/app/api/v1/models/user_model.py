import enum
from typing import Optional

import sqlalchemy as db
from fastapi import HTTPException
from sqlalchemy import Enum, event, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates, relationship, Session

from api.v1.schemas.data_types import PhoneStr, PasswordStr
from core.babel_config import _
from core.security import hash_password
from utils import cypher
from utils.uuid6 import uuid7
from .base_model import BaseModel, base_validate_positive
from ..exceptions import CustomValidationError
from sqlalchemy_utils import URLType


class GenderEnum(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'


SUPERUSER = 'superuser'
STUDENT = 'student'
CURATOR = 'curator'
MENTOR = 'mentor'
DIRECTOR = 'director'


class User(BaseModel):
    id = db.Column(UUID, primary_key=True, default=uuid7)
    user_id = db.Column(db.Integer)
    birthday = db.Column(db.Date)
    region_id = db.Column(db.Integer, db.ForeignKey("region.id"))
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    gender = db.Column(Enum(GenderEnum), default=GenderEnum.MALE)
    phone = db.Column(db.String, index=True)  # don't set unique=True
    email = db.Column(db.String, index=True)  # don't set unique=True
    hashed_password = db.Column(db.String, nullable=False)
    image_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE", name="fk_user_image"))
    created_by_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="SET NULL"))
    is_superuser = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    organization_id = db.Column(UUID,
                                db.ForeignKey("organization.id", name="fk_organization_users", ondelete="RESTRICT"))
    salt = db.Column(db.LargeBinary, unique=True)
    last_login = db.Column(db.DateTime)
    google_user_id = db.Column(db.String)
    github_login = db.Column(db.String)

    translations = relationship('UserTranslation', backref='translation', cascade="all,delete")
    image = relationship("Media", foreign_keys=[image_id], backref="user_image", cascade="all,delete")
    roles = relationship("Role", secondary='link_user_role', back_populates='users', )
    self_permissions = relationship("Permission", secondary='link_user_permission', back_populates='users')

    mentor_course = relationship("Course", secondary="link_mentor_course", back_populates="mentors",
                                 cascade="all,delete")

    mentor_info = relationship("MentorInfo", back_populates='user', uselist=False, )

    organization = relationship("Organization", foreign_keys=[organization_id], back_populates="users", )

    notifications = relationship("Notification", back_populates="receiver", cascade="all,delete",
                                 foreign_keys="[Notification.receiver_id]",
                                 primaryjoin="and_(Notification.receiver_id==User.id, Notification.is_read==False)")

    __table_args__ = (
        db.CheckConstraint('num_nulls(email, phone) < 2', name="Email or phone required check"),
    )
    user_first_name = association_proxy('translations', 'first_name')
    user_last_name = association_proxy('translations', 'last_name')
    user_short_name = association_proxy('translations', 'short_name')

    def __repr__(self):
        return f"<User {self.id}>"

    @property
    def full_name(self):
        if self.user_first_name and self.user_last_name:
            return f"{self.user_first_name[0]} {self.user_last_name[0]}"
        elif self.user_last_name:
            return self.user_last_name[0]
        elif self.user_first_name:
            return self.user_first_name[0]
        else:
            return None

    @validates('phone')
    def validate_phone(self, key, value):
        if value:
            return PhoneStr.validate(value)
        return value

    @validates('hashed_password')
    def validate_and_hash_password(self, key, value):
        validated_password = PasswordStr.validate(value)
        self.salt = cypher.encrypt_pass(validated_password)
        return hash_password(validated_password)

    @hybrid_property
    def permissions(self):
        return list(set([perm for perm in self.role_permissions] +
                        [perm for perm in self.self_permissions]))

    @hybrid_property
    def role_permissions(self):
        return [permission for role in self.roles for permission in role.permissions]

    def add_permissions(self, permissions_list: list[str], db_session: Optional[Session] = None):
        import fastapi_sqlalchemy
        from api.v1 import crud
        db_session = db_session or fastapi_sqlalchemy.db.session
        permissions_objs = [permission for title in permissions_list if
                            (permission := crud.permission.get_obj(where={Permission.title: title},
                                                                   db_session=db_session))]
        self.self_permissions.extend(permissions_objs)
        db_session.add(self)
        db_session.commit()

    def get_curator(self, course_id: int, db_session: Optional[Session] = None) -> Optional["User"]:
        from api.v1 import crud
        from .course_model import CourseGroup, LinkCourseGroupStudent
        stmt = select(CourseGroup) \
            .where(CourseGroup.course_id == course_id) \
            .join(LinkCourseGroupStudent, onclause=LinkCourseGroupStudent.course_group_id == CourseGroup.id) \
            .where(LinkCourseGroupStudent.student_id == self.id)
        course_group = crud.course_group.get(query=stmt, db_session=db_session)
        return course_group.curator if course_group else None


def check_email_and_phone(mapper, connection, target):
    if not target.email and not target.phone:
        raise CustomValidationError(_("Email or phone required"))

    # check email
    if target.email:
        stmt = select(User.__table__.columns.id).where(User.email == target.email)
        if target.id:
            stmt = stmt.where(User.id != target.id)
        objs = connection.execute(stmt)
        users = objs.mappings().all()
        if users:
            raise HTTPException(409, _("email already exists in database"))
    # check phone
    if target.phone:
        stmt = select(User.__table__.columns.id).where(User.phone == target.phone)
        if target.id:
            stmt = stmt.where(User.id != target.id)
        objs = connection.execute(stmt)
        users = objs.mappings().all()
        if users:
            raise HTTPException(409, _("phone already exists in database"))


event.listen(User, 'before_insert', check_email_and_phone)
event.listen(User, 'before_update', check_email_and_phone)


class UserTranslation(BaseModel):
    first_name = db.Column(db.String, index=True)
    last_name = db.Column(db.String, index=True)
    short_name = db.Column(db.String, index=True)
    street = db.Column(db.String, index=True)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    language = relationship("Language")
    __table_args__ = (
        db.UniqueConstraint('user_id', 'language_id'),
    )


class Organization(BaseModel):
    id = db.Column(UUID, primary_key=True, default=uuid7)
    director_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"))
    logo_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE"))
    created_by_id = db.Column(UUID, db.ForeignKey("user.id"))
    legal_address_region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    legal_address_district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    identification_number = db.Column(db.Integer, nullable=False, unique=True)
    bank_account = db.Column(db.String(16))
    bank_mfo = db.Column(db.String(5))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    brand_name = db.Column(db.String)
    domain_name = db.Column(URLType)

    translations = relationship('OrganizationTranslation', backref='translation', cascade="all,delete")

    logo = relationship("Media", backref="organization_logo", cascade="all,delete")
    legal_address_region = relationship("Region", backref="organization", )
    legal_address_district = relationship("District", backref="organization", )
    users = relationship('User', back_populates='organization',
                         primaryjoin="User.organization_id == Organization.id")
    director = relationship("User", foreign_keys=[director_id])
    allowed_courses = relationship("Course", secondary="link_organization_allowed_course",
                                   back_populates="allowed_organizations")


class OrganizationTranslation(BaseModel):
    title = db.Column(db.String, index=True)
    is_active = db.Column(db.Boolean, default=True)
    organization_id = db.Column(UUID, db.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'language_id'),
    )


class District(BaseModel):
    sort = db.Column(db.Integer, default=1)
    code = db.Column(db.Integer, index=True)
    is_active = db.Column(db.Boolean, default=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id', ondelete="CASCADE"), nullable=False)

    translations = relationship('DistrictTranslation', backref='translation', cascade="all,delete")

    __table_args__ = (db.CheckConstraint(sort > 0, name='check_sort_positive'), {})

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


class DistrictTranslation(BaseModel):
    title = db.Column(db.String, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('district_id', 'language_id'),
    )


class Region(BaseModel):
    sort = db.Column(db.Integer, default=1)
    code = db.Column(db.Integer, index=True)
    is_active = db.Column(db.Boolean, default=True)

    districts = relationship("District", backref="region", cascade="all,delete")
    translations = relationship('RegionTranslation', backref='translation', cascade="all,delete")

    __table_args__ = (db.CheckConstraint(sort > 0, name='check_sort_positive'), {})

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


class RegionTranslation(BaseModel):
    title = db.Column(db.String, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('region_id', 'language_id'),
    )


class Role(BaseModel):
    title = db.Column(db.String, nullable=False, unique=True, index=True)
    desc = db.Column(db.String, index=True)
    is_active = db.Column(db.Boolean, default=True)
    organization_id = db.Column(UUID, db.ForeignKey("organization.id"), nullable=False)

    permissions = relationship("Permission", secondary='link_role_permission', back_populates='roles', )
    users = relationship("User", secondary='link_user_role', back_populates='roles', )

    def add_permissions(self, permissions_list: list[str], db_session: Optional[Session] = None):
        from api.v1 import crud
        import fastapi_sqlalchemy
        db_session = db_session or fastapi_sqlalchemy.db.session

        permissions_objs = [permission for title in permissions_list if
                            (permission := crud.permission.get_obj(where={Permission.title: title},
                                                                   db_session=db_session))]
        self.permissions.extend(permissions_objs)
        db_session.add(self)
        db_session.commit()


class Permission(BaseModel):
    title = db.Column(db.String, nullable=False, unique=True, index=True)
    desc = db.Column(db.String, index=True)
    is_active = db.Column(db.Boolean, default=True)

    roles = relationship("Role", secondary='link_role_permission', back_populates='permissions')
    users = relationship("User", secondary='link_user_permission', back_populates='self_permissions')

    @staticmethod
    def check_permission(user: User, perm_title: str):
        # Check if superuser
        if user.is_superuser:
            return

        # Check role permissions
        if perm_title not in [perm.title for perm in user.permissions]:
            raise HTTPException(403, _("You have not a permission to perform action."))


class LinkUserRole(BaseModel):
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)


class LinkUserPermission(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete="CASCADE"), nullable=False)


class LinkRolePermission(BaseModel):
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete="CASCADE"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete="CASCADE"), nullable=False)


class Contact(BaseModel):
    name = db.Column(db.String, nullable=False, index=True)
    phone = db.Column(db.String, nullable=False, index=True)
    text = db.Column(db.String, index=True)
    created_by_id = db.Column(UUID, db.ForeignKey("user.id"))
    image_id = db.Column(UUID, db.ForeignKey("media.id"))


class StudentInfo(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False, unique=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor_info.id'), nullable=False)

    mentor = relationship("MentorInfo", backref='student_info')
    user = relationship("User", backref="student_info", uselist=False)
    translations = relationship('StudentInfoTranslation', backref='translation', cascade="all,delete")


class StudentInfoTranslation(BaseModel):
    student_info_id = db.Column(db.Integer, db.ForeignKey('student_info.id', ondelete="CASCADE"), nullable=False)
    personal_note = db.Column(db.String)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('student_info_id', 'language_id'),
    )


class CuratorInfo(BaseModel):
    user_id = db.Column(db.UUID, db.ForeignKey('user.id'), nullable=False, unique=True)
    contract_number = db.Column(db.String)

    user = relationship("User", backref="curator_info", )
    translations = relationship('CuratorInfoTranslation', backref='translation', cascade="all,delete")


class CuratorInfoTranslation(BaseModel):
    curator_info_id = db.Column(db.Integer, db.ForeignKey('curator_info.id', ondelete="CASCADE"), nullable=False)
    education_and_career = db.Column(db.String)
    about_choosing_profession = db.Column(db.String)
    projects_and_portfolios = db.Column(db.String)
    advice_to_students = db.Column(db.String)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('curator_info_id', 'language_id'),
    )


class MentorInfo(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False, unique=True)
    contract_number = db.Column(db.String)
    level = db.Column(db.String, nullable=False)
    main_work = db.Column(db.String, nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    resume_id = db.Column(db.UUID, db.ForeignKey('media.id'))

    user = relationship("User", back_populates="mentor_info", )
    resume = relationship("Media")
    translations = relationship('MentorInfoTranslation', backref='translation', cascade="all,delete")


class MentorInfoTranslation(BaseModel):
    mentor_info_id = db.Column(db.Integer, db.ForeignKey('mentor_info.id', ondelete="CASCADE"), nullable=False)
    education_and_career = db.Column(db.String)
    about_choosing_profession = db.Column(db.String)
    projects_and_portfolios = db.Column(db.String)
    advice_to_students = db.Column(db.String)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('mentor_info_id', 'language_id'),
    )


class LinkMentorCourse(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete="CASCADE"), nullable=False)


class CuratorWeekends(BaseModel):
    curator_id = db.Column(db.UUID, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.Date, nullable=False)


class CuratorVacation(BaseModel):
    desc = db.Column(db.String)
    start = db.Column(db.Date, nullable=False)
    stop = db.Column(db.Date, nullable=False)

# https://github.com/tsatsujnr139/fastapi-role-based-access-control-auth-service/
