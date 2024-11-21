from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from .. import db
from typing import Optional


class ComplaintStatusEnum(Enum):
    confirmed = "confirmed"
    pending = "pending"
    rejected = "rejected"


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    complaint_text = Column(Text, nullable=False)
    status = db.Column(
        db.Enum(ComplaintStatusEnum), default=ComplaintStatusEnum.pending
    )
    resolved_at = Column(TIMESTAMP, nullable=True)
    admin_notes = Column(Text)

    # Use string-based relationship
    user = relationship("User", back_populates="complaints")
    item = relationship("Item", back_populates="complaints")

    def __init__(
        self,
        user_id: Column[int] | int,
        item_id: int,
        complaint_text: str,
        status: ComplaintStatusEnum =ComplaintStatusEnum.pending,
        resolved_at: Optional[datetime]=None,
        admin_notes: Optional[str] =None,
    ):
        self.user_id = user_id
        self.item_id = item_id
        self.complaint_text = complaint_text
        self.status = status
        self.resolved_at = resolved_at
        self.admin_notes = admin_notes
