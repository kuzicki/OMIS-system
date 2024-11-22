from flask import Blueprint, render_template, redirect, url_for, session, request, flash

from ..services.item_service import ItemService
from ..services.user_service import UserService
from ..services.favorite_service import FavoriteService
from ..services.complaint_service import ComplaintService
from ..services.transaction_service import TransactionService, TransactionError

from ..models.category import Category
from ..models.item import Item
from ..models.user import User, UserRoleEnum

from .. import db


user_routes = Blueprint("user_routes", __name__)


def check_user_session():
    if "user_id" not in session:
        return redirect(url_for("auth_routes.welcome"))

    if not UserService.is_valid(session["user_id"]):
        return redirect(url_for("auth_routes.welcome"))

    if UserService.is_blocked(session["user_id"]):
        return render_template("blocked.html")

    if UserService.is_admin(session["user_id"]):
        return redirect(url_for("admin_routes.panel"))

    return None


@user_routes.route("/find")
def find():
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    selected_category_id = request.args.get("category")
    search_term = request.args.get("search", "")
    transaction_type = request.args.get("transaction_type", "both")
    sort_by = request.args.get("sort_by", "price")
    sort_order = request.args.get("sort_order", "asc")

    items, selected_category, categories = ItemService.get_find_results(
        selected_category_id, search_term, transaction_type, sort_by, sort_order
    )
    user_currency = UserService.get_currency(session["user_id"])
    return render_template(
        "user_find.html",
        categories=categories,
        selected_category=selected_category,
        items=items,
        user_currency=user_currency,
    )


@user_routes.route("/my-items")
def items():
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response
    items = ItemService.get_user_items(session["user_id"])
    user_currency = UserService.get_currency(session["user_id"])

    return render_template("user_items.html", items=items, user_currency=user_currency)


@user_routes.route("/remove-item/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    if ItemService.remove_item(item_id, session["user_id"]):
        return redirect(url_for("user_routes.items"))

    return redirect(url_for("user_routes.items"))


@user_routes.route("/buy/<int:item_id>", methods=["POST"])
def buy(item_id):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response
    res = TransactionService.buy_item(session["user_id"], item_id)
    if res is None:
        return redirect(url_for("user_routes.find"))
    elif res is TransactionError.NotEnoughCurrency:
        session["error_message"] = "Not enough currency to buy the item"
    elif res is TransactionError.NotValidRequest:
        session["error_message"] = "Not valid user or item"
    elif res is TransactionError.TheOwnerCantBuyHisOwn:
        session["error_message"] = "The owner can't buy his own item"

    return redirect(url_for(f"user_routes.view_item", item_id=item_id))


@user_routes.route("/add-item", methods=["GET", "POST"])
def add_item():
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    user_currency = UserService.get_currency(session["user_id"])
    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        category_str = request.form.get("category", "")
        category_id = int(category_str) if category_str else None
        item_type = request.form["item_type"]
        description = request.form["description"]
        file_path, image_path = ItemService.upload_new_files(
            name, request.files["upload_file"], request.files["image"]
        )

        new_item = Item(
            title=name,
            price=int(price),
            category_id=category_id,
            item_type=item_type,
            description=description,
            owner_id=session["user_id"],
            file_link=file_path,
            image_link=image_path,
        )

        ItemService.add_item(new_item)

        categories = Category.query.filter_by(parent_id=None).all()
        return render_template(
            "add_item.html", categories=categories, user_currency=user_currency
        )

    categories = Category.query.all()
    return render_template(
        "add_item.html", categories=categories, user_currency=user_currency
    )


@user_routes.route("/update-item/<int:item_id>", methods=["POST"])
def update_item(item_id):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    item = ItemService.get_item(item_id)
    if item is None:
        return redirect(url_for("user_routes.find"))

    item.title = request.form["title"]
    item.price = int(request.form["price"])

    file_path, image_path = ItemService.upload_new_files(
        request.form["title"], request.files["file"], request.files["image"]
    )
    category_str = request.form.get("category", "")
    item.category_id = int(category_str) if category_str else None
    item.item_type = request.form["item_type"]
    item.description = request.form["description"]

    if file_path:
        item.file_link = file_path
    if image_path:
        item.image_link = image_path

    db.session.commit()

    return redirect(url_for("user_routes.edit_item", item_id=item_id))


@user_routes.route("/edit-item/<int:item_id>", endpoint="edit_item")
def edit_item(item_id):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    item = ItemService.get_item(item_id)
    if item is None:
        return redirect(url_for("user_routes.find"))

    user = UserService.get_user(id=session["user_id"])
    file_preview = ItemService.get_preview(item_id)
    error_message = session.pop("error_message", None)

    categories = Category.query.filter_by(parent_id=None).all()
    user_currency = UserService.get_currency(session["user_id"])
    return render_template(
        "user_edit_item.html",
        item=item,
        user=user,
        file_preview=file_preview,
        error_message=error_message,
        categories=categories,
        user_currency=user_currency,
    )


@user_routes.route("/view-item/<int:item_id>", endpoint="view_item")
def view_item(item_id):
    if "user_id" not in session:
        return redirect(url_for("auth_routes.welcome"))

    if UserService.is_blocked(session["user_id"]):
        return render_template("blocked.html")

    if not UserService.is_valid(session["user_id"]):
        return redirect(url_for("auth_routes.welcome"))

    item = Item.query.filter_by(id=item_id).first()

    if item is None:
        return redirect(url_for("user_routes.find"))

    user = UserService.get_user(id=session["user_id"])
    file_preview = ItemService.get_preview(item_id)
    favorite = FavoriteService.is_favorite(session["user_id"], item_id)
    error_message = session.pop("error_message", None)
    user_currency = UserService.get_currency(session["user_id"])
    return render_template(
        "user_view_item.html",
        item=item,
        user=user,
        file_preview=file_preview,
        favorite=favorite,
        error_message=error_message,
        user_currency=user_currency,
    )


@user_routes.route("/view-user/<int:user_id>")
def view_profile(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth_routes.welcome"))

    if UserService.is_blocked(session["user_id"]):
        return render_template("blocked.html")

    if not UserService.is_valid(session["user_id"]):
        return redirect(url_for("auth_routes.welcome"))

    items = ItemService.get_user_items(user_id)
    user = UserService.get_user(id=user_id)

    admin = UserService.get_user(id=session["user_id"])
    is_admin = admin.role.value
    user_currency = UserService.get_currency(session["user_id"])

    return render_template(
        "user_view_profile.html",
        items=items,
        user=user,
        is_admin=is_admin,
        user_currency=user_currency,
    )


@user_routes.route("/profile", methods=["GET", "POST"])
def profile():
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response
    user_currency = UserService.get_currency(session["user_id"])
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        nickname = request.form["nickname"]
        user = UserService.get_user(session["user_id"])
        if not UserService.update_profile(
            session["user_id"], full_name, nickname, email
        ):
            return render_template(
                "user_profile.html",
                user=user,
                error_message="Failed to update the changes",
                user_currency=user_currency,
            )
        else:
            return render_template(
                "user_profile.html",
                user=user,
                message="Successfully updated the profile",
                user_currency=user_currency,
            )

    user = UserService.get_user(session["user_id"])
    return render_template("user_profile.html", user=user, user_currency=user_currency)


@user_routes.route("/favorites")
def favorite():
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    items = FavoriteService.get_favorite(session["user_id"])
    user_currency = UserService.get_currency(session["user_id"])

    return render_template("favorites.html", items=items, user_currency=user_currency)


@user_routes.route("/remove-favorite/<int:item_id>", methods=["POST"])
def remove_favorite(item_id: int):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    FavoriteService.remove_favorite(session["user_id"], item_id)

    return redirect(url_for("user_routes.favorite"))


@user_routes.route("/add-favorite/<int:item_id>", methods=["POST"])
def add_favorite(item_id: int):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    FavoriteService.add_favorite(session["user_id"], item_id)

    return redirect(url_for("user_routes.view_item", item_id=item_id))


@user_routes.route("/make-complaint/<int:item_id>", methods=["GET", "POST"])
def make_complaint(item_id: int):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response
    message = None
    if request.method == "POST":
        if ComplaintService.make_complaint(item_id, request.form["complaint_reason"]):
            message = "The complaint has been submitted!"
        else:
            message = "The complaint isn't sumbitted"

    item = ItemService.get_item(item_id)

    user_currency = UserService.get_currency(session["user_id"])
    return render_template("user_make_complaint.html", item=item, message=message, user_currency=user_currency)


@user_routes.route("/offer-trade/<int:item_id>", methods=["GET", "POST"])
def offer_trade(item_id: int):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response
    error_message = None
    message = None

    if request.method == "POST":
        exchange_id = int(request.form["exchange_item_id"])
        res = TransactionService.offer_trade(session["user_id"], exchange_id, item_id)
        if res is TransactionError.TheOwnerCantOfferToHimself:
            error_message = "Tried offering the item to himself"
        elif res is TransactionError.NotValidRequest:
            error_message = "Not valid request"
        elif res is TransactionError.DuplicateTransaction:
            error_message = "There's already such transaction"
        elif res is None:
            message = "Offer has been sent"

    items = ItemService.get_my_items_for_trade(session["user_id"], item_id)
    user_currency = UserService.get_currency(session["user_id"])

    return render_template(
        "user_offer_trade.html",
        items=items,
        item_id=item_id,
        message=message,
        error_message=error_message,
        user_currency=user_currency
    )


@user_routes.route("/trade")
def trade():
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    trades = TransactionService.get_pending_trades(session["user_id"])

    trade_details = []
    for trade in trades:
        buyer = User.query.get(trade.buyer_id)
        exchange_item = Item.query.get(trade.exchange_id)
        item = Item.query.get(trade.item_id)
        if item is None or buyer is None:
            continue

        trade_details.append(
            {
                "buyer_name": buyer.nickname,
                "exchange_item": exchange_item,
                "exchange_item_id": exchange_item.id if exchange_item else None,
                "item": item,
                "item_id": item.id,
                "trade_id": trade.id,
            }
        )

    message = session.pop("message", None)
    error_message = session.pop("error_message", None)
    user_currency = UserService.get_currency(session["user_id"])
    return render_template(
        "user_trades.html",
        trade_details=trade_details,
        message=message,
        error_message=error_message,
        user_currency=user_currency
    )


@user_routes.route("/accept-trade/<int:item_id>", methods=["POST"])
def accept_trade(item_id: int):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response
    res = TransactionService.accept_trade(item_id)

    if res is None:
        session["message"] = "Accepted trade"
    elif res is TransactionError.DatabaseError:
        session["error_message"] = "Something went wrong"
    elif res is TransactionError.TradeNotFound:
        session["erorr_message"] = "Trade wasn't found"

    return redirect(url_for("user_routes.trade"))


@user_routes.route("/decline-trade/<int:item_id>", methods=["POST"])
def decline_trade(item_id: int):
    redirect_response = check_user_session()
    if redirect_response:
        return redirect_response

    res = TransactionService.decline_trade(item_id)
    if res is None:
        session["message"] = "Accepted trade"
    elif res is TransactionError.DatabaseError:
        session["error_message"] = "Something went wrong"
    elif res is TransactionError.TradeNotFound:
        session["erorr_message"] = "Trade wasn't found"

    return redirect(url_for("user_routes.trade"))
