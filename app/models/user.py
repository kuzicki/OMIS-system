from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .. import db

class UserRoleEnum(Enum):
    user = "user"
    admin = "admin"

class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(255))
    full_name = Column(String(255))
    profile_picture = Column(String(255))
    is_blocked = Column(Boolean, default=False)
    blocked_until = Column(TIMESTAMP, nullable=True)
    role = db.Column(db.Enum(UserRoleEnum), default=UserRoleEnum.user)

    currency = Column(Integer, default=1000000000)
    description = Column(Text)

    # Use string-based relationships
    complaints = relationship("Complaint", back_populates="user")
    items = relationship("Item", back_populates="owner")

    def __init__(
        self, 
        email: str, 
        password_hash: str, 
        nickname: str, 
        full_name: Optional[str] = None, 
        profile_picture: Optional[str] = None, 
        is_blocked: bool = False, 
        blocked_until: Optional[datetime] = None, 
        role: UserRoleEnum = UserRoleEnum.user, 
        currency: Optional[int] = None, 
        description: Optional[str] = None
    ):
        self.email = email
        self.password_hash = password_hash
        self.nickname = nickname
        self.full_name = full_name
        self.profile_picture = profile_picture
        self.is_blocked = is_blocked
        self.blocked_until = blocked_until
        self.role = role
        self.currency = currency
        self.description = description
