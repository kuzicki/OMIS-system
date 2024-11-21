from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    Enum,
    TIMESTAMP,
    ForeignKey,
)
from typing import Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime, timezone
from .. import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    buyer_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    seller_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    price = Column(Integer, nullable=False)
    exchange_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=True
    )
    transaction_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))

    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    item = relationship("Item", foreign_keys=[item_id])
    exchange_item = relationship("Item", foreign_keys=[exchange_id])


    def __init__(
        self,
        buyer_id: int,
        seller_id: int,
        item_id: int,
        price: int,
        exchange_id: Optional[int] = None,
        transaction_type: str = "buy",
        status: str = "pending",
        created_at: Optional[datetime] = None,
    ):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.item_id = item_id
        self.price = price
        self.exchange_id = exchange_id
        self.transaction_type = transaction_type
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
