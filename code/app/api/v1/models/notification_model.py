import enum
from sqlalchemy import Enum
import sqlalchemy as db
from sqlalchemy.orm import relationship, validates, backref
from sqlalchemy.dialects.postgresql import UUID
from .base_model import BaseModel
from api.v1.schemas.data_types import PhoneStr


class Notification(BaseModel):
    sender_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(UUID, db.ForeignKey("user.id"), nullable=False)
    is_send = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    content = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    sender = relationship("User", backref=backref("sent_notifications", cascade="all,delete"),
                          foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="notifications",
                            foreign_keys=[receiver_id])


class SmsStatusEnum(str, enum.Enum):
    SUCCESS = 'success'
    WAITING = 'waiting'
    PROCESSING = 'processing'
    FAILED = 'failed'


class SentSms(BaseModel):
    count = db.Column(db.Integer)
    text = db.Column(db.String)
    sms_id = db.Column(UUID)
    status = db.Column(Enum(SmsStatusEnum), default=SmsStatusEnum.WAITING)
    phone = db.Column(db.String)
    created_by_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="SET NULL"))
    organization_id = db.Column(UUID, db.ForeignKey("organization.id", ondelete="SET NULL"))
    is_active = db.Column(db.Boolean, default=True)

    @validates('phone')
    def validate_phone(self, key, value):
        return PhoneStr.validate(value)


class ConnectedNotification(BaseModel):
    user_id = db.Column(UUID, db.ForeignKey("user.id", ondelete="CASCADE"), unique=True)

    homework_via_telegram = db.Column(db.Boolean, default=False)
    homework_via_email = db.Column(db.Boolean, default=False)
    homework_via_platform = db.Column(db.Boolean, default=True)

    platform_updates_via_telegram = db.Column(db.Boolean, default=False)
    platform_updates_via_email = db.Column(db.Boolean, default=False)
    platform_updates_via_platform = db.Column(db.Boolean, default=False)

    promotions_and_offers_via_telegram = db.Column(db.Boolean, default=False)
    promotions_and_offers_via_email = db.Column(db.Boolean, default=False)
    promotions_and_offers_via_platform = db.Column(db.Boolean, default=False)

    other_news_via_telegram = db.Column(db.Boolean, default=False)
    other_news_via_email = db.Column(db.Boolean, default=False)
    other_news_via_platform = db.Column(db.Boolean, default=False)
