from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def initialize_models():
    from .models.user import User
    from .models.complaint import Complaint
    from .models.item import Item
    from .models.category import Category
    from .models.transaction import Transaction
    from .models.favorite import Favorite
    from .services.user_service import UserService

