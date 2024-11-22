from typing import Optional, List
from enum import Enum
from datetime import datetime, timezone, timedelta
from sqlalchemy import exists
from sqlalchemy.sql.operators import is_not
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.sql import expression
from sqlalchemy.orm import joinedload
from ..models.user import User, UserRoleEnum
from ..models.item import Item
from ..models.complaint import Complaint, ComplaintStatusEnum
from ..models.favorite import Favorite
from ..models.transaction import Transaction
from ..services.user_service import UserService
from ..services.item_service import ItemService

from .. import db


class ComplaintResolution(Enum):
    Confirmed = ("confirmed",)
    Rejected = "rejected"


class ComplaintService:
    @staticmethod
    def make_complaint(item_id: int, complaint_text: str) -> bool:
        item = ItemService.get_item(item_id)
        if item is None:
            return False

        complaint = Complaint(item.owner_id, item_id, complaint_text)

        db.session.add(complaint)
        db.session.commit()
        return True

    @staticmethod
    def decline_complaint(complaint_id: int):
        complaint: Optional[Complaint] = Complaint.query.get(complaint_id)
        if complaint is None:
            return
        complaint.status = ComplaintStatusEnum.rejected
        complaint.resolved_at = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def accept_complaint(complaint_id: int, admin_notes: str):
        complaint = Complaint.query.get(complaint_id)
        if complaint is None:
            return
        complaint.status = ComplaintStatusEnum.confirmed
        complaint.admin_notes = admin_notes
        complaint.resolved_at = datetime.now(timezone.utc)

        user = User.query.get(complaint.item.owner_id)
        user.is_blocked = True

        utc_now = datetime.now(timezone.utc)
        utc_plus_one_day = utc_now + timedelta(days=1)
        user.blocked_until = utc_plus_one_day
        db.session.commit()


    @staticmethod
    def get_unresolved() -> List[Complaint]:
        return (
            db.session.query(Complaint)
            .join(User, Complaint.user_id == User.id)
            .join(Item, Complaint.item_id == Item.id)
            .options(joinedload(Complaint.user), joinedload(Complaint.item))
            .filter(User.is_blocked == False)
            .filter(User.role != UserRoleEnum.admin)
            .filter(Complaint.status == "pending")
            .filter(Item.owner_id.isnot(None))
            .all()
        )

    @staticmethod
    def get_id(complaint_id: int) -> Optional[Complaint]:
        return Complaint.query.get(complaint_id)
