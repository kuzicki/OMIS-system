from ..models.user import User, UserRoleEnum
from ..models.item import Item
from typing import Optional
from .. import db
from enum import Enum
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone


def unblock_users():
    from main import app
    with app.app_context():
        current_time = datetime.now(timezone.utc)
        users_to_unblock = User.query.filter(
            User.is_blocked == True, User.blocked_until <= current_time
        ).all()
        for user in users_to_unblock:
            user.is_blocked = False
            user.blocked_until = None

        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(unblock_users, "interval", minutes=10)
scheduler.start()

class PromoteUserResult(Enum):
    NoUser = ("There's no such user",)
    AlreadyPromoted = "The user is already promoted"


class UserService:
    @staticmethod
    def create_user(email: str, password_hash: str, nickname: str) -> User:
        new_user = User(email=email, password_hash=password_hash, nickname=nickname)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def login(email: str, password_hash: str) -> Optional[User]:
        return User.query.filter_by(email=email, password_hash=password_hash).first()

    @staticmethod
    def exists(email: str) -> bool:
        return User.query.filter_by(email=email).first() is not None

    @staticmethod
    def is_admin(id: int) -> bool:
        user = User.query.get(id)
        if user:
            return user.role == UserRoleEnum.admin

        return False

    @staticmethod
    def is_blocked(id: int) -> bool:
        user = User.query.get(id)
        if user:
            return user.is_blocked

        return False

    @staticmethod
    def is_valid(id: int) -> bool:
        user = User.query.get(id)
        if user is not None:
            return True

        return False


    @staticmethod
    def get_user(id: int) -> Optional[User]:
        return User.query.get(id)

    @staticmethod
    def update_profile(id: int, full_name: str, nickname: str, email: str) -> bool:
        user = UserService.get_user(id)
        if user is None:
            return False

        user.email = email
        user.full_name = full_name
        user.nickname = nickname
        db.session.commit()
        return True

    @staticmethod
    def get_currency(user_id: int) -> Optional[int]:
        user: Optional[User] = User.query.get(user_id)
        if user:
            return user.currency

        return None

    @staticmethod
    def promote_user(user_email: str) -> Optional[PromoteUserResult]:
        user = User.query.filter_by(email=user_email).first()

        if user is None:
            return PromoteUserResult.NoUser
        if user.role == UserRoleEnum.admin:
            return PromoteUserResult.AlreadyPromoted

        user.role = "admin"
        db.session.commit()

        return None
