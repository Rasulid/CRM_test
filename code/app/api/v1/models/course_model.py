import enum
import uuid

import sqlalchemy as db
from fastapi import HTTPException
from slugify import slugify
from sqlalchemy import Enum, event, func, select, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates, backref, object_session
from sqlalchemy_utils import URLType

from api.v1.exceptions import CustomValidationError
from core.babel_config import _
from .base_model import BaseModel, base_validate_positive
from .media_model import Media
from .payment_model import Discount


class BaseCourseModel(BaseModel):
    __abstract__ = True

    is_active = db.Column(db.Boolean, default=True)
    sort = db.Column(db.Integer, default=1)
    slug = db.Column(db.String, nullable=False, unique=True)

    # @staticmethod
    # def create_slug(mapper, connection, target):
    #     pass
    #
    # @classmethod
    # def __declare_last__(cls):
    #     event.listen(cls, 'after_insert', cls.create_slug)

    # __table_args__ = (db.CheckConstraint(sort > 0, name='check_sort_positive'), {})

    @declared_attr
    def __table_args__(cls):
        db.CheckConstraint(cls.sort > 0, name='check_sort_positive'), {}

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)

    @validates('price')
    def validate_price(self, key, value):
        if value < 0:
            raise CustomValidationError(_('price value invalid'))
        return value


class BaseCourseTranslationModel(BaseModel):
    __abstract__ = True

    title = db.Column(db.String, nullable=False, index=True)
    desc = db.Column(db.String, index=True)

    @declared_attr
    def language_id(cls):
        return db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)


class Profession(BaseCourseModel):
    """ Kasblar:
            1. Dasturlash
            2. Dizayn
            3. Marketing
            4. Analitika
    """
    # translations = relationship("ProfessionTranslation", backref="profession", cascade='all,delete')

    # @staticmethod
    # def create_slug(mapper, connection, target):
    #     query = select(ProfessionTranslation).where(ProfessionTranslation.profession_id == target.id)
    #     print(query)
    #     response = connection.execute(query)
    #     print(response)
    #     obj = response.scalar_one_or_none()
    #     print(obj)
    #     # if not target.slug:
    #     target.slug = slugify.slugify(obj.title)

    topics = relationship("Topic", backref="profession", cascade="all,delete")
    translations = relationship('ProfessionTranslation', backref='profession',
                                cascade="all,delete")


@event.listens_for(Profession, 'before_insert')
def profession_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.translations[0].title)


class ProfessionTranslation(BaseCourseTranslationModel):
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id', ondelete='CASCADE'), nullable=False)
    profession = relationship(Profession, back_populates="translations")

    __table_args__ = (
        db.UniqueConstraint('profession_id', 'language_id'),
    )


class Topic(BaseCourseModel):
    profession_id = db.Column(db.Integer, db.ForeignKey("profession.id", ondelete="CASCADE"))

    categories = relationship("Category", backref="topic", cascade="all,delete")
    translations = relationship('TopicTranslation', backref='translation', cascade="all,delete")


@event.listens_for(Topic, 'before_insert')
def topic_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.translations[0].title)


class TopicTranslation(BaseCourseTranslationModel):
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('topic_id', 'language_id'),
    )


class Category(BaseCourseModel):
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), nullable=False)
    logo_id = db.Column(UUID, db.ForeignKey(Media.id))

    courses = relationship("Course", secondary='link_category_course', back_populates='categories',
                           cascade="all, delete")
    logo = relationship("Media", foreign_keys=[logo_id], backref="category_logo", )
    translations = relationship('CategoryTranslation', backref='translation', cascade="all,delete")


@event.listens_for(Category, 'before_insert')
def category_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.translations[0].title)


class CategoryTranslation(BaseCourseTranslationModel):
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('category_id', 'language_id'),
    )


class CourseStatusEnum(str, enum.Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PREMIERE = 'premiere'


class DifficultyLevelEnum(str, enum.Enum):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    EXPERT = 'expert'


class Course(BaseCourseModel):
    created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
    price = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), nullable=False)
    is_free = db.Column(db.Boolean, default=False)
    banner_image_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE"))
    banner_file_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE"))
    trailer_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE"))
    organization_id = db.Column(UUID, db.ForeignKey("organization.id"), nullable=False)
    status = db.Column(Enum(CourseStatusEnum), default=CourseStatusEnum.PUBLIC)
    is_verified = db.Column(db.Boolean, default=False)
    is_for_child = db.Column(db.Boolean, default=False)
    level = db.Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.BEGINNER)
    discount_id = db.Column(db.ForeignKey(Discount.id))
    duration = db.Column(db.Integer)
    telegram_url = db.Column(URLType)
    # course_old_id = db.Column(db.Integer)  # Vaqtincha
    language_id = db.Column(db.ForeignKey("language.id", ondelete="SET NULL"), nullable=False)

    categories = relationship("Category", secondary='link_category_course', back_populates='courses', )
    translations = relationship('CourseTranslation', backref='translation', cascade="all,delete")
    created_by = relationship("User", backref="course")
    organization = relationship("Organization", backref="course")
    discount = relationship("Discount", backref="course")
    promocodes = relationship("Promocode", secondary="link_course_promocode", back_populates="courses", )
    tag = relationship("Tag", secondary="link_course_tag", back_populates="course", )
    course_modules = relationship("CourseModule",
                                  backref=backref("course"),
                                  order_by=lambda: CourseModule.__table__.columns.sort.asc())
    allowed_users = relationship("User", secondary="link_user_allowed_course",
                                 backref=backref("allowed_courses"))
    allowed_organizations = relationship("Organization", secondary="link_organization_allowed_course",
                                         back_populates="allowed_courses")
    mentors = relationship("User", secondary="link_mentor_course", back_populates="mentor_course", )

    groups = relationship("CourseGroup", back_populates="course", cascade="all,delete")

    banner_image = relationship("Media", foreign_keys=[banner_image_id], backref="course_banner_image", )
    banner_file = relationship("Media", foreign_keys=[banner_file_id], backref="course_banner_file",
                               )
    trailer = relationship("Media", foreign_keys=[trailer_id], backref="course_trailer", )
    ratings = relationship("CourseRating", backref="course")
    language = relationship("Language")

    reviews = relationship("CourseReview", back_populates="course",
                           cascade="all,delete",
                           primaryjoin="and_(CourseReview.course_id==Course.id, CourseReview.is_verified==True)")
    user_purchases = relationship("UserPurchase", back_populates="course")

    __table_args__ = (db.CheckConstraint(price >= 0, name='check_price_valid'), {})

    @hybrid_property
    def course_blocks(self):
        return {'course_about_block': self.course_about_block, 'course_whom_block': self.course_whom_block,
                'course_learn_block': self.course_learn_block, 'course_plan_block': self.course_plan_block,
                'student_work_block': self.course_students_work_block}

    @hybrid_property
    def total_modules(self) -> int:
        db_session = object_session(self)
        res = db_session.query(func.count(CourseModule.id)).where(CourseModule.course_id == self.id).filter_by(
            is_active=True)
        return res.scalar() or 0

    @hybrid_property
    def total_lessons(self) -> int:
        db_session = object_session(self)
        stmt = db_session.query(
            func.count(CourseLesson.id)
        ).select_from(Course).where(Course.id == self.id).join(CourseModule).join(
            CourseLesson).filter_by(is_active=True)
        res = db_session.execute(stmt)
        return res.scalar() or 0

    @hybrid_property
    def total_homeworks(self) -> int:
        db_session = object_session(self)
        stmt = db_session.query(func.count(CourseLesson.id)).select_from(CourseModule).where(
            CourseModule.course_id == self.id).join(CourseLesson).filter_by(is_active=True, is_homework=True)
        res = db_session.execute(stmt)
        return res.scalar() or 0

    @property
    def rating(self) -> float:
        db_session = object_session(self)
        stmt = db_session.query(func.avg(CourseRating.rating)).where(CourseRating.course_id == self.id)
        res = db_session.execute(stmt)
        return float(round(res.scalar() or 0, 1))


@event.listens_for(Course, 'before_insert')
def course_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.translations[0].title)


class CourseTranslation(BaseCourseTranslationModel):
    sub_title = db.Column(db.String)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'language_id'),
    )


class LinkCategoryCourse(BaseModel):
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)


class CourseModule(BaseCourseModel):
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="RESTRICT"), nullable=False)
    is_free = db.Column(db.Boolean, default=False)
    price = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), default=0)
    # level = db.Column(postgresql.ENUM(DifficultyLevelEnum, create_type=False, checkfirst=True, inherit_schema=True),
    #                   default=DifficultyLevelEnum.beginner)
    level = db.Column(Enum(DifficultyLevelEnum), default=DifficultyLevelEnum.BEGINNER)
    discount_id = db.Column(db.ForeignKey("discount.id"))
    is_final = db.Column(db.Boolean, default=False, server_default=db.false())

    translations = relationship('CourseModuleTranslation', backref='translation', cascade="all,delete")
    promocodes = relationship("Promocode", secondary="link_course_module_promocode", back_populates="course_modules",
                              )
    discount = relationship("Discount", backref="course_module", )
    course_lessons = relationship("CourseLesson",
                                  backref=backref("course_module", ),
                                  order_by=lambda: CourseLesson.__table__.columns.sort.asc())

    allowed_users = relationship("User", secondary="link_user_allowed_course_module",
                                 cascade="all,delete", backref=backref("allowed_course_modules",
                                                                       cascade="all,delete"))

    __table_args__ = (db.CheckConstraint(price >= 0, name='check_price_valid'), {})

    @property
    def course_lesson_count(self):
        return len(self.course_lessons)

    @hybrid_property
    def total_lessons(self):
        return sum([1 for lesson in self.course_lessons if lesson.is_active])

    @hybrid_property
    def total_homeworks(self):
        return sum([1 for lesson in self.course_lessons if lesson.is_homework])


@event.listens_for(CourseModule, 'before_insert')
def course_module_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.translations[0].title)


class CourseModuleTranslation(BaseCourseTranslationModel):
    content = db.Column(db.String)
    course_module_id = db.Column(db.Integer, db.ForeignKey("course_module.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_module_id', 'language_id'),
    )


class CourseLesson(BaseCourseModel):
    course_module_id = db.Column(db.Integer, db.ForeignKey('course_module.id', ondelete="RESTRICT"), nullable=False)
    is_free = db.Column(db.Boolean, default=False)
    is_homework = db.Column(db.Boolean, default=False)
    price = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), default=0)
    video_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE"))

    discount_id = db.Column(db.ForeignKey("discount.id"))
    lesson_id = db.Column(db.Integer)
    is_final = db.Column(db.Boolean, default=False, server_default=db.false())

    translations = relationship('CourseLessonTranslation', backref='translation', cascade="all,delete")
    promocodes = relationship("Promocode", secondary="link_course_lesson_promocode", back_populates="course_lessons",
                              )
    discount = relationship("Discount", backref="course_lesson", )

    allowed_users = relationship("User", secondary="link_user_allowed_course_lesson",
                                 cascade="all,delete", backref=backref("allowed_course_lessons",
                                                                       cascade="all,delete"))
    attachments = relationship('Media', secondary="course_lesson_media", backref='course_lesson',

                               cascade="all,delete")

    ks_uuids = relationship('CourseLessonVideo', backref='course_lesson',
                            foreign_keys="[CourseLessonVideo.course_lesson_id]")
    learned_users = relationship("UserLearnedCourseLesson", backref=backref("course_lesson"), cascade="all,delete")

    __table_args__ = (db.CheckConstraint(price >= 0, name='check_price_valid'), {})

    @hybrid_property
    def blocks(self):
        return {'training_block': self.training_block,
                'video_block': self.video_block,
                'text_block': self.text_block,
                'file_block': self.file_block,
                'quiz_block': self.quiz_block}

    @property
    def duration(self):
        video_blocks_duration = object_session(self).query(func.sum(VideoBlock.duration)).where(
            VideoBlock.course_lesson_id == self.id).scalar()
        lesson_video_duration = object_session(self).query(func.sum(CourseLessonVideo.duration)).where(
            CourseLessonVideo.course_lesson_id == self.id).scalar()
        return video_blocks_duration or lesson_video_duration or 0


@event.listens_for(CourseLesson, 'before_insert')
def course_lesson_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.translations[0].title)


class CourseLessonTranslation(BaseCourseTranslationModel):
    content = db.Column(db.String)
    course_lesson_id = db.Column(db.Integer, db.ForeignKey("course_lesson.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_lesson_id', 'language_id'),
    )


class CourseLessonVideo(BaseModel):
    course_lesson_id = db.Column(db.Integer, db.ForeignKey('course_lesson.id', ondelete="CASCADE"), nullable=False)
    ks_uuid = db.Column(db.String, nullable=False)
    duration = db.Column(db.Float)
    sort = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, server_default=db.true(), default=True)

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


class CourseLessonMedia(BaseModel):
    media_id = db.Column(UUID, db.ForeignKey('media.id'), nullable=False)
    course_lesson_id = db.Column(db.Integer, db.ForeignKey('course_lesson.id', ondelete="CASCADE"), nullable=False)


class UserLearnedCourseLesson(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    course_lesson_id = db.Column(db.Integer, db.ForeignKey('course_lesson.id', ondelete="CASCADE"), nullable=False)
    learned_percent = db.Column(db.Float, default=0)
    is_learned = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_lesson_id'),
    )


class CourseComment(BaseModel):
    created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)  # fk(user)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    replied_by_id = db.Column(db.Integer, db.ForeignKey('course_comment.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    created_by = relationship("User", backref="course_comment", )


class CourseReview(BaseModel):
    student_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    sort = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    student = relationship("User", backref=backref("reviews", cascade="all,delete"))
    course = relationship("Course", back_populates="reviews")
    translations = relationship('CourseReviewTranslation', backref='translation',
                                cascade="all,delete")

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


class CourseReviewTranslation(BaseModel):
    text = db.Column(db.Text, nullable=False)
    course_review_id = db.Column(db.Integer, db.ForeignKey('course_review.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('course_review_id', 'language_id'),
    )


class FinalScore(BaseModel):
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    certificate_id = db.Column(db.String, unique=True, nullable=False)
    score = db.Column(db.Float, nullable=False)
    reviewed_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)

    course = relationship("Course", backref=backref("student_final_score", cascade="all,delete"))
    student = relationship("User", foreign_keys=[student_id],
                           backref=backref("final_course_score", cascade="all,delete"))

    def __init__(self, **kwargs):
        from fastapi_sqlalchemy import db
        last_certificate_id = db.session.query(FinalScore.certificate_id).order_by(
            FinalScore.id.desc()).limit(1).scalar()
        certificate_id = "{:07}".format(int(last_certificate_id) + 1)
        super().__init__(certificate_id=certificate_id, **kwargs)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'student_id'),
        db.CheckConstraint('score > 0 AND score <= 10', name='check_score_valid'),
    )


class LinkUserAllowedCourse(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id'),
    )


class LinkUserAllowedCourseModule(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    course_module_id = db.Column(db.Integer, db.ForeignKey("course_module.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_module_id'),
    )


class LinkUserAllowedCourseLesson(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    course_lesson_id = db.Column(db.Integer, db.ForeignKey("course_lesson.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_lesson_id'),
    )


class Language(BaseModel):
    """
    Language model
    O'zbek tili - uz
    Rus tili - ru
    Ingliz tili - en
    """
    title = db.Column(db.JSON, nullable=False)
    code = db.Column(db.String, nullable=False, unique=True, index=True)
    flag_id = db.Column(UUID, db.ForeignKey("media.id"))
    is_active = db.Column(db.Boolean, default=True)

    flag = relationship("Media")

    @validates('code')
    def validate_code(self, key, code) -> str:
        if code and len(code) <= 2:
            return code
        raise HTTPException(400, _('enter code in ISO 639-1 format. For example: en'))


class Tag(BaseModel):
    title = db.Column(db.String, nullable=False, index=True)
    slug = db.Column(db.String, nullable=False, unique=True, index=True)

    course = relationship("Course", secondary="link_course_tag", back_populates="tag", )


@event.listens_for(Tag, 'before_insert')
def tag_before_insert_event(mapper, connect, target):
    if not target.slug:
        target.slug = slugify(target.title)


class LinkCourseTag(BaseModel):
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)


# ================== About Course Blocks ====================

class BaseAboutCourseBlock(BaseModel):
    __abstract__ = True

    is_active = db.Column(db.Boolean, default=True)

    @declared_attr
    def course_id(cls):
        return db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)


class AboutCourseFormatBlock(BaseAboutCourseBlock):
    """ О формате курса """
    courses = relationship("Course", backref=backref("course_about_block", cascade="all,delete"),
                           )
    translations = relationship('AboutCourseFormatBlockTranslation', backref='translation',
                                cascade="all,delete")


class AboutCourseFormatBlockTranslation(BaseModel):
    key = db.Column(db.String, nullable=False, index=True)  # Длительность
    value = db.Column(db.String, nullable=False, index=True)  # 4 месяца
    parent_id = db.Column(db.Integer, db.ForeignKey('about_course_format_block.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('parent_id', 'language_id'),
    )


class ForWhomCourseBlock(BaseAboutCourseBlock):
    """ Кому подойдет курс? """
    courses = relationship("Course", backref=backref("course_whom_block", cascade="all,delete"),
                           )
    translations = relationship('ForWhomCourseBlockTranslation', backref='translation',
                                cascade="all,delete")


class ForWhomCourseBlockTranslation(BaseModel):
    whom = db.Column(db.String, nullable=False, index=True)  # Будущим программистам
    desc = db.Column(db.String, nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('for_whom_course_block.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('parent_id', 'language_id'),
    )


class WhatLearnCourseBlock(BaseAboutCourseBlock):
    """ Чему вы научитесь """
    courses = relationship("Course", backref=backref("course_learn_block", cascade="all,delete"),
                           )
    translations = relationship('WhatLearnCourseBlockTranslation', backref='translation',
                                cascade="all,delete")


class WhatLearnCourseBlockTranslation(BaseModel):
    title = db.Column(db.String, nullable=False, index=True)  # Основы Java
    desc = db.Column(db.String, nullable=False, index=True)  # Соединение с данными на другом сервере
    parent_id = db.Column(db.Integer, db.ForeignKey('what_learn_course_block.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('parent_id', 'language_id'),
    )


class CoursePlanBlock(BaseAboutCourseBlock):
    """ План курса """
    courses = relationship("Course", backref=backref("course_plan_block", cascade="all,delete"),
                           )
    translations = relationship('CoursePlanBlockTranslation', backref='translation',
                                cascade="all,delete")


class CoursePlanBlockTranslation(BaseModel):
    key = db.Column(db.String, nullable=False, index=True)  # Теория
    value = db.Column(db.String, nullable=False, index=True)  # Теоретические знания важны для любой области.
    parent_id = db.Column(db.Integer, db.ForeignKey('course_plan_block.id', ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('parent_id', 'language_id'),
    )


class CourseStudentsWorkBlock(BaseAboutCourseBlock):
    """ Проекты выпускников """
    student_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"),
                           nullable=False)
    media_id = db.Column(UUID, db.ForeignKey("media.id", ondelete="CASCADE"))
    courses = relationship("Course", backref=backref("course_students_work_block",
                                                     cascade="all,delete"), )

    media = relationship("Media", backref="work_block_media", cascade="all,delete")
    student = relationship("User", backref="work_block_student")


class CourseGroup(BaseModel):
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    curator_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    is_main = db.Column(db.Boolean, default=False, server_default=db.false())

    course = relationship("Course", back_populates="groups", )

    curator = relationship("User", backref=backref('curator_groups', cascade="all,delete"),
                           foreign_keys=[curator_id])

    students = relationship("User", secondary="link_course_group_student",
                            backref=backref('student_groups', cascade="all,delete"))

    organization_id = db.Column(UUID, db.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'course_id', 'curator_id'),
    )


class LinkCourseGroupStudent(BaseModel):
    course_group_id = db.Column(db.Integer, db.ForeignKey('course_group.id'), nullable=False)
    student_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)


class CourseRating(BaseModel):
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.SmallInteger)

    user = relationship("User")
    __table_args__ = (
        db.UniqueConstraint('course_id', 'user_id'),
        db.CheckConstraint('rating > 0 AND rating <= 5', name='check_rating_valid'),
    )

    @validates('rating')
    def validate_rating(self, key, value) -> str:
        if 0 < value <= 5:
            return value
        raise HTTPException(400, _('Value should be from 1 to 5'))


# ========== Course Lesson contents ============

class BaseCourseLessonBlock(BaseModel):
    __abstract__ = True

    is_active = db.Column(db.Boolean, default=True)
    sort = db.Column(db.Integer, default=1)

    @declared_attr
    def course_lesson_id(cls):
        return db.Column(db.Integer, db.ForeignKey("course_lesson.id", ondelete="CASCADE"), nullable=False)

    @declared_attr
    def created_by_id(cls):
        return db.Column(UUID, db.ForeignKey("user.id"), nullable=False)

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


class Training(BaseModel):
    title = db.Column(db.String, nullable=False, unique=True, index=True)
    example = db.Column(db.Text, nullable=False)
    case_count = db.Column(db.Integer, nullable=False, default=1)
    input_id = db.Column(UUID, db.ForeignKey('media.id'))
    output_id = db.Column(UUID, db.ForeignKey('media.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)

    input = relationship("Media", foreign_keys=[input_id], cascade="all,delete")
    output = relationship("Media", foreign_keys=[output_id], cascade="all,delete")


class TrainingBlock(BaseCourseLessonBlock):
    training_id = db.Column(db.Integer, db.ForeignKey("training.id", ondelete="CASCADE"), nullable=False)

    course_lesson = relationship("CourseLesson", backref=backref("training_block", cascade="all,delete"))
    training = relationship("Training", backref=backref("training_block", cascade="all,delete"))


class VideoBlock(BaseCourseLessonBlock):
    ks_uuid = db.Column(db.String, nullable=False)
    duration = db.Column(db.Float)

    course_lesson = relationship("CourseLesson", backref=backref("video_block", cascade="all,delete"))


class TextBlock(BaseCourseLessonBlock):
    course_lesson = relationship("CourseLesson", backref=backref("text_block", cascade="all,delete"))
    translations = relationship('TextBlockTranslation', backref='translation',
                                cascade="all,delete")


class TextBlockTranslation(BaseModel):
    content = db.Column(db.Text, nullable=False)
    text_block_id = db.Column(db.Integer, db.ForeignKey("text_block.id"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('text_block_id', 'language_id'),
    )


class FileBlock(BaseCourseLessonBlock):
    media_id = db.Column(UUID, db.ForeignKey('media.id'))

    course_lesson = relationship("CourseLesson", backref=backref("file_block", cascade="all,delete"))

    media = relationship("Media", foreign_keys=[media_id], cascade="all,delete")


class QuizBlockTypeEnum(str, enum.Enum):
    LAST_PUBLIC = 'last_public'
    EVERY_PUBLIC = 'every_public'
    LAST_PRIVATE = 'last_private'
    EVERY_PRIVATE = 'every_private'


class QuizBlock(BaseCourseLessonBlock):
    quiz_type = db.Column(Enum(QuizBlockTypeEnum), nullable=False)
    allowed_attempts = db.Column(db.Integer)
    fixed_seconds = db.Column(db.Integer)
    allowed_errors_count = db.Column(db.Integer)
    course_lesson = relationship("CourseLesson", backref=backref("quiz_block", cascade="all,delete"))
    questions = relationship("Question", secondary='link_quiz_block_question', back_populates='quiz_blocks')

    @validates('allowed_attempts', 'fixed_seconds', 'allowed_errors_count')
    def validate_fields(self, key, value):
        return base_validate_positive(key, value)


# ========== Quiz Q/A contents ============

class QuestionTypeEnum(str, enum.Enum):
    SINGLE = 'single'
    MULTIPLE = 'multiple'
    OWN_ANSWER = 'own_answer'


class Question(BaseModel):
    type = db.Column(Enum(QuestionTypeEnum), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="SET NULL"))

    translations = relationship('QuestionTranslation', backref='translation',
                                cascade="all,delete")
    quiz_blocks = relationship("QuizBlock", secondary='link_quiz_block_question', back_populates='questions')
    answers = relationship("Answer", backref="question", cascade="all, delete")

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


class QuizBlockQuestionSort(BaseModel):
    quiz_block_id = db.Column(db.Integer, db.ForeignKey("quiz_block.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    sort = db.Column(db.Integer, default=1)

    __table_args__ = (
        db.UniqueConstraint('question_id', 'quiz_block_id'),
    )


class QuestionTranslation(BaseModel):
    title = db.Column(db.String, nullable=False, index=True)
    content = db.Column(db.Text, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id', ondelete="CASCADE"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('question_id', 'language_id'),
    )


class LinkQuizBlockQuestion(BaseModel):
    quiz_block_id = db.Column(db.Integer, db.ForeignKey('quiz_block.id', ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete="CASCADE"), nullable=False)


class UserOwnAnswer(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    answer = db.Column(db.String, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id', ondelete="CASCADE"), nullable=False)


class Answer(BaseModel):
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort = db.Column(db.Integer, default=1)
    created_by_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="SET NULL"))

    translations = relationship('AnswerTranslation', backref='translation',
                                cascade="all,delete")

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)


def is_correct_event(mapper, connection, target):
    print("Event is_correct", target.is_correct)
    if target.is_correct:
        question_type = connection.execute(
            select(Question.type).where(Question.id == target.question_id)).scalar_one_or_none()
        if question_type and question_type == QuestionTypeEnum.SINGLE:
            answers = connection.execute(
                select(Answer.id).where(Answer.id != target.id, Answer.question_id == target.question_id,
                                        Answer.is_correct == db.true())
            ).scalars().all()

            if answers:
                raise CustomValidationError("Correct answer already exists!")


event.listen(Answer, 'before_insert', is_correct_event)
event.listen(Answer, 'before_update', is_correct_event)


class AnswerTranslation(BaseModel):
    title = db.Column(db.String, nullable=False, index=True)
    answer_id = db.Column(db.Integer, db.ForeignKey("answer.id", ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id', ondelete="CASCADE"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('answer_id', 'language_id'),
    )


# between filter by created_at
# https://stackoverflow.com/questions/33826441/return-average-of-counts-of-records-after-a-group-by-statement


class LinkOrganizationAllowedCourse(BaseModel):
    organization_id = db.Column(UUID, db.ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'course_id'),
    )
