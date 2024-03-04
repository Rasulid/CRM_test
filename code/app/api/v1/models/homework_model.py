import datetime
import enum
from typing import Optional

import sqlalchemy as db
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates, backref, Session

from api.v1.celery_tasks import send_notification
from utils.uuid6 import uuid7
from .base_model import BaseModel, base_validate_positive


class HomeworkStatusEnum(str, enum.Enum):
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    WAITING = 'waiting'


class Homework(BaseModel):
    id = db.Column(UUID, primary_key=True, default=uuid7)
    course_lesson_id = db.Column(db.Integer, db.ForeignKey("course_lesson.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    sort = db.Column(db.Integer, default=1)
    status = db.Column(Enum(HomeworkStatusEnum), default=HomeworkStatusEnum.WAITING)
    closed_by_id = db.Column(UUID, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    check_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    course_lesson = relationship("CourseLesson",
                                 backref=backref("course_lesson_homework", cascade="all,delete"),
                                 )

    closed_by = relationship("User", backref=backref('homework_closed_by', cascade="all,delete"),
                             foreign_keys=[closed_by_id])
    student = relationship("User", backref=backref('homework_student', cascade="all,delete"),
                           foreign_keys=[student_id])

    homework_messages = relationship("HomeworkMessage", backref='homework', cascade="all,delete")

    __table_args__ = (
        db.CheckConstraint(sort > 0, name='check_sort_positive'),
        db.UniqueConstraint('course_lesson_id', 'student_id'),
    )

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)

    @hybrid_property
    def count_messages(self):
        return len(self.homework_messages)

    def change_status(self, curator_id: UUID, status: HomeworkStatusEnum, closed_by_id: UUID,
                      db_session: Optional[Session] = None):
        import fastapi_sqlalchemy
        db_session = db_session or fastapi_sqlalchemy.db.session
        print(59, status, self.status)
        if status == HomeworkStatusEnum.ACCEPTED:
            print(61, self.student_id, curator_id, self.id)
            self.closed_by_id = closed_by_id

            send_notification.apply_async(kwargs={"sender_id": curator_id,
                                                  "receiver_id": self.student_id,
                                                  "homework_id": self.id})

            # crud.notification.send(sender_id=curator_id, receiver_id=self.student_id, homework=self)
        elif status == HomeworkStatusEnum.REJECTED:
            print(67, self.student_id, curator_id, self.id)
            send_notification.apply_async(kwargs={"sender_id": curator_id,
                                                  "receiver_id": self.student_id,
                                                  "homework_id": self.id})
            # crud.notification.send(sender_id=curator_id, receiver_id=self.student_id, homework=self)
        else:
            if len(self.homework_messages) == 1:
                print(71, self.student_id, curator_id, self.id)
                # agar birinchi xabar bo'lsa
                send_notification.apply_async(kwargs={"sender_id": self.student_id,
                                                      "receiver_id": curator_id,
                                                      "homework_id": self.id})
                # crud.notification.send(sender_id=self.student_id, receiver_id=curator_id, homework=self)
                self.check_date = datetime.datetime.utcnow()
            elif self.status != HomeworkStatusEnum.WAITING:
                print(76, self.student_id, curator_id, self.id)
                self.check_date = datetime.datetime.utcnow()
                send_notification.apply_async(kwargs={"sender_id": self.student_id,
                                                      "receiver_id": curator_id,
                                                      "homework_id": self.id})
        self.status = status
        db_session.add(self)
        db_session.commit()


class HomeworkMessage(BaseModel):
    id = db.Column(UUID, primary_key=True, default=uuid7)
    created_by_id = db.Column(UUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    homework_id = db.Column(UUID, db.ForeignKey('homework.id', ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    created_by = relationship("User", backref=backref('created_by_user', cascade="all,delete"),
                              )
    media_files = relationship("HomeworkMedia", backref='homework', cascade="all,delete")


# @event.listens_for(HomeworkMessage, 'after_insert')
# def change_hw_last_msg_created_at_event(mapper, connection, target):
#     connection.execute(
#         Homework.__table__.update().
#             where(Homework.id == target.homework_id).
#             values(last_msg_created_at=datetime.datetime.now())
#     )


class HomeworkMedia(BaseModel):
    media_id = db.Column(UUID, db.ForeignKey('media.id', ondelete="CASCADE"), nullable=False)
    homework_message_id = db.Column(UUID, db.ForeignKey('homework_message.id', ondelete="CASCADE"), nullable=False)
    sort = db.Column(db.Integer, default=1)

    media = relationship("Media", backref='homework_media', cascade="all,delete")

    @validates('sort')
    def validate_sort(self, key, value):
        return base_validate_positive(key, value)
