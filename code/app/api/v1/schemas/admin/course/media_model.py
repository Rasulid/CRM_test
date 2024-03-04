from api.v1.models import BaseModel
import sqlalchemy as db
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from utils.uuid6 import uuid7
from sqlalchemy import event


class Media(BaseModel):
    id = db.Column(UUID, primary_key=True, default=uuid7)
    filename = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=True, unique=True)
    size = db.Column(db.Integer, nullable=True)
    file_format = db.Column(db.String, nullable=False)
    created_by_id = db.Column(UUID, db.ForeignKey('user.id', name="fk_media_created_by", ondelete="SET NULL"))
    is_active = db.Column(db.Boolean, default=True)

    created_by = relationship("User", foreign_keys=[created_by_id], backref=backref("media", cascade="all, delete"))


# @event.listens_for(Media, 'after_delete')
# def after_delete_media(mapper, connection, target):
#     from api.v1.deps import minio_auth
#     if target.path:
#         minio_client = minio_auth()
#         minio_client.remove_object(target.path)
