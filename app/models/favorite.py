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
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime, timezone
from .. import db

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    
    # Ensures that the same product is not added to favorites multiple times by the same user
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='unique_user_product'),
    )

    def __init__(self, user_id: int, product_id: int):
        self.user_id = user_id
        self.product_id = product_id
