from ..services.item_service import ItemService
from ..services.user_service import UserService
from ..models.user import User, UserRoleEnum
from ..models.item import Item
from ..models.transaction import Transaction
from typing import Optional, List
from enum import Enum
from .. import db
from sqlalchemy.exc import NoResultFound


class TransactionError(Enum):
    NotValidRequest = (1,)
    NotEnoughCurrency = (2,)
    TheOwnerCantBuyHisOwn = (3,)
    TheOwnerCantOfferToHimself = (4,)
    DuplicateTransaction = (5,)
    TradeNotFound = (6,)
    DatabaseError = 7


class TransactionService:
    @staticmethod
    def buy_item(id: int, item_id: int) -> Optional[TransactionError]:
        user = User.query.get(id)
        item = Item.query.get(item_id)
        if user is None or item is None:
            return TransactionError.NotValidRequest
        if user.id == item.owner_id:
            return TransactionError.TheOwnerCantBuyHisOwn
        currency = user.currency
        if currency >= item.price:
            user.currency -= item.price

            transaction = Transaction(
                buyer_id=user.id,
                seller_id=item.owner_id,
                item_id=item.id,
                price=item.price,
                transaction_type="buy",
                status="completed",
            )
            db.session.add(transaction)

            item.owner_id = None

            db.session.commit()

            return None

        return TransactionError.NotEnoughCurrency

    @staticmethod
    def offer_trade(
        user_id: int, exchange_id: int, item_id: int
    ) -> Optional[TransactionError]:
        user = User.query.get(user_id)
        exchange_item = Item.query.get(exchange_id)
        item = Item.query.get(item_id)
        if user is None or item is None or exchange_item is None:
            return TransactionError.NotValidRequest
        if user.id == item.owner_id:
            return TransactionError.TheOwnerCantOfferToHimself
        existing_transaction = Transaction.query.filter_by(
            buyer_id=user.id,
            seller_id=item.owner_id,
            item_id=item.id,
            exchange_id=exchange_id,
            transaction_type="trade",
            status="pending"
        ).first()
        if existing_transaction:
            return TransactionError.DuplicateTransaction

        transaction = Transaction(
            buyer_id=user.id,
            seller_id=item.owner_id,
            item_id=item.id,
            price=item.price,
            exchange_id=exchange_id,
            transaction_type="trade",
            status="pending",
        )
        db.session.add(transaction)
        db.session.commit()

        return None

    @staticmethod
    def get_pending_trades(user_id: int) -> List[Transaction]:
        trades = (
            Transaction.query.join(User, User.id == Transaction.seller_id)
            .filter(
                Transaction.seller_id == user_id,
                Transaction.status == "pending",
                User.is_blocked.is_(False),
                User.role != UserRoleEnum.admin
            )
            .all()
        )

        return trades

    @staticmethod
    def accept_trade(transaction_id: int) -> Optional[TransactionError]:
        try:
            transaction = db.session.query(Transaction).filter_by(id=transaction_id).one()

            transaction.status = "completed"

            db.session.query(Transaction).filter(
                Transaction.status == "pending",
                Transaction.item_id == transaction.item_id,
                Transaction.id != transaction.id
            ).update({"status": "rejected"}, synchronize_session=False)

            item = ItemService.get_item(transaction.item_id)
            item.owner_id = None
            exchange_item = ItemService.get_item(transaction.exchange_id)
            exchange_item.owner_id = None
            db.session.commit()
        except NoResultFound:
            return TransactionError.TradeNotFound
        except Exception as e:
            print(e)
            db.session.rollback()
            return TransactionError.DatabaseError
        return None

    @staticmethod
    def decline_trade(transaction_id: int) -> Optional[TransactionError]:
        try:
            transaction = (
                db.session.query(Transaction).filter_by(id=transaction_id).one()
            )

            transaction.status = "rejected"
            db.session.commit()
        except NoResultFound:
            return TransactionError.TradeNotFound
        except Exception as _:
            db.session.rollback()
            return TransactionError.DatabaseError
        return None
