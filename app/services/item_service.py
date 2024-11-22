from werkzeug.datastructures import FileStorage

from ..services.user_service import UserService
from ..models.user import User, UserRoleEnum
from ..models.item import Item
from ..models.transaction import Transaction
from ..models.category import Category
from typing import Optional, Tuple, List
from .. import db
import os
from datetime import datetime
from sqlalchemy.sql import expression
from sqlalchemy import or_, and_

SAVED_IMAGES = ".\\static\\images"
SAVED_FILES = "D:\\Uni\\sem5\\omis\\saved\\files\\"


class ItemService:
    @staticmethod
    def get_item(id: int) -> Optional[Item]:
        return Item.query.get(id)

    @staticmethod
    def get_preview(id: int) -> Optional[str]:
        item = Item.query.get(id)
        if item is None:
            return None

        if item.file_link is not None:
            with open(item.file_link, "r", encoding="UTF-8") as file:
                file_preview = file.read(500)
            return file_preview

        return None

    @staticmethod
    def get_all_available_products():
        return (
            db.session.query(Item)
            .join(User, Item.owner_id == User.id)
            .filter(
                User.is_blocked == expression.false(), User.role != UserRoleEnum.admin
            )
            .all()
        )

    @staticmethod
    def remove_item(item_id: int, owner_id: int) -> bool:
        item = Item.query.filter_by(id=item_id, owner_id=owner_id).first()

        if item is None:
            return False

        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def add_item(new_item: Item):
        db.session.add(new_item)
        db.session.commit()

    @staticmethod
    def get_user_items(user_id: int) -> List[Item]:
        items = Item.query.filter_by(owner_id=user_id).all()
        return items

    @staticmethod
    def upload_new_files(
        name: str, file: FileStorage, image: FileStorage
    ) -> Tuple[str | None, str | None]:
        file_path = None
        image_path = None

        if file:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Timestamp format
            file_extension = file.filename.rsplit(".", 1)[1].lower()
            file_filename = f"file_{name}_{timestamp}.{file_extension}"
            file_path = os.path.join(SAVED_FILES, file_filename)
            file.save(file_path)

        if image:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Timestamp format
            image_extension = image.filename.rsplit(".", 1)[1].lower()
            image_filename = f"image_{name}_{timestamp}.{image_extension}"
            image_path = os.path.join(SAVED_IMAGES, image_filename)
            image.save(image_path)
            image_path = image_filename

        return file_path, image_path

    @staticmethod
    def get_my_items(user_id: int) -> List[Item]:
        return Item.query.filter_by(owner_id=user_id).all()

    @staticmethod
    def get_find_results(
        selected_category_id: Optional[str],
        search_term: str,
        transaction_type: str,
        sort_by: str,
        sort_order: str,
    ) -> Tuple[List[Item], Optional[Category], List[Category]]:

        categories = Category.query.filter_by(parent_id=None).all()
        selected_category = None
        if selected_category_id:
            selected_category = Category.query.get(selected_category_id)

        if selected_category_id:
            subcategory_ids = [
                id
                for id, in db.session.query(Category.id).filter(
                    Category.parent_id == selected_category_id
                )
            ]

        items_query = Item.query.join(
            User,
            and_(
                Item.owner_id == User.id,
                User.is_blocked == False,
                User.role != UserRoleEnum.admin,
            ),
        )

        if search_term != "":
            items_query = items_query.filter(Item.title.contains(search_term))

            items_query = items_query.filter(
                or_(
                    Item.category_id == selected_category_id,
                    Item.category_id.in_(subcategory_ids),
                )
            )

        if transaction_type != "both":
            items_query = items_query.filter(Item.item_type == transaction_type)

        if sort_by == "price":
            if sort_order == "asc":
                items_query = items_query.order_by(Item.price.asc())
            else:
                items_query = items_query.order_by(Item.price.desc())
        elif sort_by == "created_at":
            if sort_order == "asc":
                items_query = items_query.order_by(Item.created_at.asc())
            else:
                items_query = items_query.order_by(Item.created_at.desc())

        items = items_query.all()
        return (items, selected_category, categories)

    @staticmethod
    def get_my_items_for_trade(user_id: int, item_id: int) -> List[Item]:
        subquery = (
            db.session.query(Transaction.exchange_id)
            .filter(
                (
                    (Transaction.item_id == item_id)
                    | (Transaction.exchange_id == item_id)
                ),
                Transaction.status == "pending",
                Transaction.exchange_id.isnot(None),  # Exclude NULL exchange IDs
            )
            .subquery()
        )

        # Query to get all items owned by the user that are not in the subquery
        available_items = Item.query.filter(
            Item.owner_id == user_id,
            Item.id.notin_(subquery),  # Ensure items aren't in the subquery
        ).all()

        return available_items
