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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime, timezone
from .. import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    
    # Self-referential relationship: category can have subcategories
    parent = relationship('Category', remote_side=[id], backref='subcategories')
