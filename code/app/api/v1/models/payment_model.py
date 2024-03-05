import enum
import math
from typing import Optional

import sqlalchemy as db
from sqlalchemy import Enum, event, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates, backref

from api.v1.exceptions import CustomValidationError
from core.babel_config import _
from db.session import engine
from utils.uuid6 import uuid7
from .base_model import BaseModel
# from .course_model import Course


# class PaymentProvidersEnum(str, enum.Enum):
#     CLICK = 'click'
#     PAYCOM = 'paycom'
#     UZUM = 'uzum'
#     UPAY = 'upay'
#     RAHMAT = "rahmat"
#
#
# class PaymentTypeEnum(str, enum.Enum):
#     CASH = "cash"
#     PLASTIC = "plastic"
#
#
# class Promocode(BaseModel):
#     id = db.Column(UUID, primary_key=True, default=uuid7)
#     code = db.Column(db.String, nullable=False, unique=True)
#     start = db.Column(db.Date, nullable=False)
#     stop = db.Column(db.Date, nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
#     created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
#     discount_id = db.Column(UUID, db.ForeignKey("discount.id"), nullable=False)
#     is_archive = db.Column(db.Boolean, default=False)
#
#     translations = relationship('PromocodeTranslation', backref='translation', cascade="all,delete")
#     created_by = relationship("User", backref="promocode", )
#     discount = relationship("Discount", backref="promocode", uselist=False)
#
#     courses = relationship(
#         "Course", secondary="link_course_promocode", back_populates="promocodes", )
#     course_modules = relationship(
#         "CourseModule", secondary="link_course_module_promocode", back_populates="promocodes", )
#     course_lessons = relationship(
#         "CourseLesson", secondary="link_course_lesson_promocode", back_populates="promocodes", )
#
#     __table_args__ = (
#         db.CheckConstraint(start < stop, name='check_start_stop_date'),
#     )
#
#     @classmethod
#     def check_promocode(cls, code: str, course_id: Optional[int]) -> tuple[bool, Optional["Promocode"]]:
#         from api.v1 import crud
#         promocode = crud.promocode.get(where={Promocode.code: code})
#         if not promocode or not promocode.is_valid:
#             return False, None
#
#         if course_id:
#             course = crud.course.get_obj(where={Course.id: course_id})
#             if course.organization_id != promocode.created_by.organization_id:
#                 return False, None
#
#             # check organization effect
#             if not promocode.courses:
#                 return True, promocode
#
#             # check course effect
#             if course in promocode.courses:
#                 return True, promocode
#         return False, None
#
#     @validates('start', 'stop')
#     def validate_date_range(self, key, value):
#         if key == 'stop':
#             if self.start >= value:
#                 raise CustomValidationError(_('Start date should not be larger stop date'))
#         return value
#
#     @property
#     def is_valid(self):
#         if self.start >= self.stop:
#             return False
#         if self.is_archive:
#             return False
#         return self.is_active
#
#
# class PromocodeTranslation(BaseModel):
#     title = db.Column(db.String, nullable=False)
#     desc = db.Column(db.String)
#     is_active = db.Column(db.Boolean, default=True)
#     promocode_id = db.Column(UUID, db.ForeignKey("promocode.id", ondelete="CASCADE"), nullable=False)
#     language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
#
#     __table_args__ = (
#         db.UniqueConstraint('promocode_id', 'language_id'),
#     )
#

class Discount(BaseModel):
    id = db.Column(UUID, primary_key=True, default=uuid7)
    percent = db.Column(db.Float, nullable=False)
    start = db.Column(db.Date, nullable=False)
    stop = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
    is_archive = db.Column(db.Boolean, default=False)

    translations = relationship('DiscountTranslation', backref='translation', cascade="all,delete")
    created_by = relationship("User", backref="discount", )

    __table_args__ = (
        db.CheckConstraint(start < stop, name='check_start_stop_date'),
        db.CheckConstraint("0 < percent AND percent <= 100", name='check_percent'),
    )

    @validates('start', 'stop')
    def validate_date_range(self, key, value):
        if key == 'stop':
            if self.start >= value:
                raise CustomValidationError(_('Start date should not be larger stop date'))
        return value

    @validates('percent')
    def validate_percent(self, key, value):
        if not 0 < value <= 100:
            raise CustomValidationError(_("Percent should be greater 0, equal or smaller 100"))
        return value

    @property
    def is_valid(self):
        if self.start >= self.stop:
            return False
        if self.is_archive:
            return False
        return self.is_active


class DiscountTranslation(BaseModel):
    title = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    discount_id = db.Column(UUID, db.ForeignKey("discount.id", ondelete="CASCADE"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('discount_id', 'language_id'),
    )
#
#
# class LinkCoursePromocode(BaseModel):
#     promocode_id = db.Column(UUID, db.ForeignKey("promocode.id", ondelete="CASCADE"), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
#
#
# class LinkCourseModulePromocode(BaseModel):
#     promocode_id = db.Column(UUID, db.ForeignKey("promocode.id", ondelete="CASCADE"), nullable=False)
#     course_module_id = db.Column(db.Integer, db.ForeignKey("course_module.id", ondelete="CASCADE"), nullable=False)
#
#
# class LinkCourseLessonPromocode(BaseModel):
#     promocode_id = db.Column(UUID, db.ForeignKey("promocode.id", ondelete="CASCADE"), nullable=False)
#     course_lesson_id = db.Column(db.Integer, db.ForeignKey("course_lesson.id", ondelete="CASCADE"), nullable=False)
#
#
# class InstallmentPayment(BaseModel):
#     id = db.Column(UUID, primary_key=True, default=uuid7)
#     parts_count = db.Column(db.Integer, nullable=False)
#     extra_percent = db.Column(db.Float, nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
#     is_archive = db.Column(db.Boolean, default=False)
#     created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
#
#     translations = relationship('InstallmentPaymentTranslation', backref='translation',
#                                 cascade="all,delete")
#
#     __table_args__ = (
#         db.CheckConstraint("0 < extra_percent AND extra_percent <= 100", name='check_extra_percent'),
#         db.CheckConstraint(1 < parts_count, name='check_parts_count'),
#         db.UniqueConstraint('parts_count', 'extra_percent'),
#     )
#
#     @validates('extra_percent')
#     def validate_extra_percent(self, key, value):
#         if not 0 < value <= 100:
#             raise CustomValidationError(_("Extra percent should be greater 0, equal or smaller 100"))
#         return value
#
#     @validates('parts_count')
#     def validate_parts_count(self, key, value):
#         if value <= 1:
#             raise CustomValidationError(_('Installment parts should be greater than 1'))
#         return value
#
#
# class InstallmentPaymentTranslation(BaseModel):
#     installment_payment_id = db.Column(UUID, db.ForeignKey('installment_payment.id', ondelete="CASCADE"),
#                                        nullable=False)
#     title = db.Column(db.String, nullable=False)
#     desc = db.Column(db.String, nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
#     language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
#
#     __table_args__ = (
#         db.UniqueConstraint('installment_payment_id', 'language_id'),
#     )
#
#
# class Order(BaseModel):
#     created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
#     payment_provider = db.Column(Enum(PaymentProvidersEnum))
#     payment_type = db.Column(Enum(PaymentTypeEnum), nullable=False)
#     is_paid = db.Column(db.Boolean, default=False)
#     amount = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), nullable=False)
#     transaction_id = db.Column(db.String)
#     user_pay_history_id = db.Column(db.Integer, db.ForeignKey("user_pay_history.id", ondelete="CASCADE"),
#                                     nullable=False)
#
#     user_pay_history = relationship("UserPayHistory", backref=backref("order",
#                                                                       uselist=False, cascade="all, delete"),
#                                     )
#
#     __table_args__ = (db.CheckConstraint(0 <= amount, name='check_amount'), {})
#
#     @validates('amount')
#     def validate_amount(self, key, value):
#         return base_validate_not_negative(key, value)
#
#
# class UserPurchase(BaseModel):
#     course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"))
#     course_module_id = db.Column(db.Integer, db.ForeignKey("course_module.id", ondelete="CASCADE"))
#     course_lesson_id = db.Column(db.Integer, db.ForeignKey("course_lesson.id", ondelete="CASCADE"))
#
#     user_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
#     amount = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), nullable=False)
#     is_full_amount = db.Column(db.Boolean, default=False)
#     paid_percent = db.Column(db.Float, default=0)
#
#     installment_payment_id = db.Column(UUID, db.ForeignKey("installment_payment.id"))
#     promocode_id = db.Column(UUID, db.ForeignKey("promocode.id"))
#     created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
#
#     installment_payment = relationship("InstallmentPayment", backref="user_purchase", )
#     promocode = relationship("Promocode", backref="user_purchase", )
#     course = relationship("Course", back_populates="user_purchases")
#     course_module = relationship("CourseModule", backref=backref("user_purchase", ), )
#     course_lesson = relationship("CourseLesson", backref=backref("user_purchase", ), )
#     histories = relationship('UserPayHistory', backref=backref('user_purchase', ),
#                              cascade="all, delete")
#     user = relationship("User", foreign_keys=[user_id], backref=backref("user_purchase", cascade="all,delete"),
#                         )
#
#     __table_args__ = (
#         db.CheckConstraint(0 <= amount, name='check_amount'),
#         db.CheckConstraint('num_nonnulls(course_id, course_module_id, course_lesson_id) = 1'),
#         db.UniqueConstraint('course_id', 'user_id'),
#         db.UniqueConstraint('course_module_id', 'user_id'),
#         db.UniqueConstraint('course_lesson_id', 'user_id'),
#     )
#
#     @validates('amount')
#     def validate_amount(self, key, value):
#         return base_validate_not_negative(key, value)
#
#     @validates("course_id", "course_module_id", "course_lesson_id")
#     def validate_one_of_the_three(self, key, value):
#         if key == "course_lesson_id":
#             if not (self.course_id or self.course_module_id or value):
#                 raise CustomValidationError(_("One of these fields is required [Course, CourseModule, CourseLesson]"))
#             if (self.course_id and self.course_module_id) or (self.course_id and value) or (
#                     self.course_module_id and value):
#                 raise CustomValidationError(_("Choose only one field in [Course, Course Module, CourseLesson]"))
#         return value
#
#     @property
#     def all_paid_pays(self):
#         return round(sum([history.paid_money for history in self.histories if history.is_paid]), 2)
#
#     @property
#     def is_full_paid(self):
#         return round(self.all_paid_pays) == round(self.amount)
#
#
# class UserPayHistory(BaseModel):
#     user_purchase_id = db.Column(db.Integer, db.ForeignKey("user_purchase.id", ondelete="CASCADE"), nullable=False)
#     paid_money = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), nullable=False)
#     is_paid = db.Column(db.Boolean, default=False)
#     detail = db.Column(db.String)
#     created_by_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
#     paid_at = db.Column(db.DateTime)
#
#     created_by = relationship("User", backref="user_pay_history", )
#
#     __table_args__ = (
#         db.CheckConstraint(0 <= paid_money, name='check_amount'),
#     )
#
#     @validates('paid_money')
#     def validate_paid_money(self, key, value):
#         return base_validate_not_negative(key, value)


# @event.listens_for(UserPayHistory.is_paid, "set")
# target, value, old_value, initiator
# mapper, connect, target
# def is_paid_event(mapper, connection, target):
#     print("Event is_paid", target.is_paid)
#     if target.is_paid:
#         objs = connection.execute(
#             select(*UserPurchase.__table__.columns).where(UserPurchase.id == target.user_purchase_id)
#         )
#         user_purchase_dict = objs.mappings().one()
#
#         if user_purchase_dict.get('installment_payment_id', None):
#             installment_payment_id = user_purchase_dict['installment_payment_id']
#             objs = connection.execute(
#                 select(InstallmentPayment.parts_count, InstallmentPayment.extra_percent).where(
#                     InstallmentPayment.id == installment_payment_id)
#             )
#             installment_payment_dict = objs.mappings().one()
#
#             paid_percent = user_purchase_dict.get('paid_percent', 0)
#             if not paid_percent:
#                 paid_percent = 0
#
#             paid_percent += (100 / installment_payment_dict['parts_count'])
#
#             if paid_percent > 100:
#                 paid_percent = 100
#         else:
#             paid_percent = 100
#
#         connection.execute(
#             UserPurchase.__table__.update()
#             .values(paid_percent=round(paid_percent, 2))
#             .where(UserPurchase.id == target.user_purchase_id)
#         )


# event.listen(UserPayHistory, 'after_insert', is_paid_event)
# event.listen(UserPayHistory, 'after_update', is_paid_event)
#
#
# class ClickStatusEnum(str, enum.Enum):
#     PROCESSING = 'processing'
#     WAITING = "waiting"
#     CONFIRMED = 'confirmed'
#     CANCELED = 'canceled'
#     ERROR = 'error'


# class ClickTransaction(BaseModel):
#     """ Класс ClickTransaction """
#     click_trans_id = db.Column(db.String)
#     merchant_trans_id = db.Column(db.String)
#     merchant_prepare_id = db.Column(db.String)
#     sign_string = db.Column(db.String)
#     sign_datetime = db.Column(db.String)
#     click_paydoc_id = db.Column(db.String, comment="Номер платежа в системе CLICK")
#     amount = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), comment="Сумма оплаты (в сумах)")
#     action = db.Column(db.String, comment="Выполняемое действие")
#     status = db.Column(Enum(ClickStatusEnum), default=ClickStatusEnum.WAITING)
#     extra_data = db.Column(db.String)
#     message = db.Column(db.Text)
    # created_by_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    #
    # created_by = relationship("User", backref=backref("click_transaction", cascade="all,delete"), )


# class PaycomTransactionEnum(str, enum.Enum):
#     PROCESSING = 'processing'
#     SUCCESS = 'success'
#     FAILED = 'failed'
#     CANCELLED = 'cancelled'


# class PaycomTransaction(BaseModel):
#     _id = db.Column(db.String, nullable=False)
#     request_id = db.Column(db.Integer, nullable=False)
#     state = db.Column(db.Integer)
#     order_key = db.Column(db.String)
#     amount = db.Column(db.DECIMAL(precision=12, scale=2, asdecimal=False), nullable=False)
#     status = db.Column(Enum(PaycomTransactionEnum), default=PaycomTransactionEnum.PROCESSING)
#     reason = db.Column(db.Integer)
#     perform_datetime = db.Column(db.String)
#     cancel_datetime = db.Column(db.String)
#     created_datetime = db.Column(db.String)


# class UzumTransactionStatusEnum(str, enum.Enum):
#     REGISTERED = "REGISTERED"
#     AUTHORIZED = "AUTHORIZED"
#     COMPLETED = "COMPLETED"
#     REFUNDED = "REFUNDED"
#     REVERSED = "REVERSED"
#     DECLINED = "DECLINED"


# class UzumTransaction(BaseModel):
#     order_id = db.Column(db.String, nullable=False)
#     status = db.Column(db.Enum(UzumTransactionStatusEnum), nullable=False, default=UzumTransactionStatusEnum.REGISTERED)
#     action_code = db.Column(db.Integer)
#     merchant_order_id = db.Column(db.String, nullable=False)
#     amount = db.Column(db.Integer, nullable=False)
#     total_amount = db.Column(db.Integer)
#     completed_amount = db.Column(db.Integer)
#     refunded_amount = db.Column(db.Integer)
#     reversed_amount = db.Column(db.Integer)


# class UzumTransactionOperationTypeEnum(str, enum.Enum):
#     AUTHORIZE = "AUTHORIZE"
#     COMPLETE = "COMPLETE"
#     REFUND = "REFUND"
#     REVERSE = "REVERSE"
#
#
# class UzumTransactionOperationStateEnum(str, enum.Enum):
#     IN_PROGRESS = "IN_PROGRESS"
#     SUCCESS = "SUCCESS"
#     FAIL = "FAIL"


# class UzumTransactionOperation(BaseModel):
#     operation_id = db.Column(db.String, nullable=False)
#     merchant_operation_id = db.Column(db.String, nullable=False)
#     start_at = db.Column(db.String, nullable=False)
#     done_at = db.Column(db.String)
#     operation_type = db.Column(db.Enum(UzumTransactionOperationTypeEnum),
#                                default=UzumTransactionOperationTypeEnum.AUTHORIZE)
#     state = db.Column(db.Enum(UzumTransactionOperationStateEnum), default=UzumTransactionOperationStateEnum.IN_PROGRESS)
#     rrn = db.Column(db.String)
#     action_code_description = db.Column(db.String)


# class RahmatTransaction(BaseModel):
#     guid = db.Column(UUID, primary_key=True, default=uuid7)
#     uuid = db.Column(UUID)
#     is_paid = db.Column(db.Boolean, default=False)
#     is_returned = db.Column(db.Boolean, default=False)
#     merchant_order_id = db.Column(db.String, nullable=False)
#     amount = db.Column(db.Integer, nullable=False)
