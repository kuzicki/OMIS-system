from sqlalchemy import exists
from ..models.user import User, UserRoleEnum
from ..models.item import Item
from ..models.complaint import Complaint
from typing import Optional, List
from enum import Enum
from ..models.favorite import Favorite
from ..models.transaction import Transaction
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.sql import expression
from ..services.user_service import UserService
from ..services.item_service import ItemService
from sqlalchemy.orm import joinedload
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

    # @staticmethod
    # def resolve_complaint(item_id: int, admin_notes: str) -> bool:
    #
    @staticmethod
    def get_unresolved() -> List[Complaint]:
        return (
            db.session.query(Complaint)
            .join(User, Complaint.user_id == User.id)
            .join(Item, Complaint.item_id == Item.id)
            .options(joinedload(Complaint.user), joinedload(Complaint.item))
            .filter(User.is_blocked == False)
            .filter(User.role != UserRoleEnum.admin)
            .filter(Transaction.status == "pending")
            .all()
        )

    # def get_unresolved(item_id: int, admin_notes: str) -> List[Complaint]:

    @staticmethod
    def get_id(complaint_id: int) -> Optional[Complaint]:
        return Complaint.query.get(complaint_id)
