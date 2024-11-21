from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    Enum,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum
from .. import db


# Enum for transaction types
class TransactionType(Enum):
    trade = "trade"
    buy = "buy"
    both = "both"


class Item(db.Model):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    file_size = Column(Float, nullable=True)
    file_format = Column(String(50), nullable=True)
    file_link = Column(String, nullable=True)
    image_link = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    item_type = Column(
        db.Enum("trade", "buy", "both", name="transaction_type"), nullable=False
    )

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))

    owner = relationship("User", back_populates="items")
    category = relationship("Category", backref="items")
    complaints = relationship("Complaint", back_populates="item")

    def __init__(
        self,
        title: str,
        description: str,
        price: int,
        owner_id: int,
        item_type: TransactionType = TransactionType.both,
        file_size: Optional[float] = None,
        file_format: Optional[str] = None,
        file_link: Optional[str] = None,
        image_link: Optional[str] = None,
        category_id: Optional[int] = None
    ):
        self.title = title
        self.description = description
        self.file_size = file_size
        self.file_format = file_format
        self.file_link = file_link
        self.image_link = image_link
        self.price = price
        self.item_type = item_type
        self.owner_id = owner_id
        self.category_id = category_id
