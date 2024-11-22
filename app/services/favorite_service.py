from sqlalchemy import exists
from ..models.user import User, UserRoleEnum
from ..models.item import Item
from typing import Optional, List
from ..models.favorite import Favorite
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.sql import expression
from ..services.user_service import UserService
from ..services.item_service import ItemService
from .. import db


class FavoriteService:
    @staticmethod
    def get_favorite(user_id: int) -> List[Item]:
        return (
            db.session.query(Item)
            .join(Favorite, Favorite.product_id == Item.id)
            .join(User, Favorite.user_id == User.id)
            .filter(Favorite.user_id == user_id)
            .filter(User.is_blocked == expression.false())
            .filter(User.role !=  UserRoleEnum.admin)
            .filter(Item.owner_id.isnot(None))
            .all()
        )

    @staticmethod
    def remove_favorite(user_id: int, item_id: int) -> bool:
        try:
            favorite = (
                db.session.query(Favorite)
                .filter_by(user_id=user_id, product_id=item_id)
                .one()
            )
            db.session.delete(favorite)
            db.session.commit()
            return True
        except NoResultFound:
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Erorr removing favorite: {e}")
            return False

    @staticmethod
    def add_favorite(user_id: int, item_id: int) -> bool:
        item = ItemService.get_item(item_id)
        if item is None or user_id == item.owner_id:
            return False

        try:
            favorite = Favorite(user_id=user_id, product_id=item_id)
            db.session.add(favorite)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            print("Favorite already exists or violates constraints.")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error adding favorite: {e}")
            return False

    @staticmethod
    def is_favorite(user_id: int, item_id: int) -> bool:
        user = UserService.get_user(user_id)
        item = ItemService.get_item(item_id)
        if user is None or item is None:
            return True

        if user.id == item.owner_id:
            return True

        return db.session.query(
            exists().where(Favorite.user_id == user_id, Favorite.product_id == item_id)
        ).scalar()
