from flask import Flask
from app import db, initialize_models
from app.routes.auth_routes import auth_routes
from app.routes.menu_routes import menu_routes
from app.routes.user_routes import user_routes
from app.routes.admin_routes import admin_routes
from app.services.user_service import scheduler

app = Flask(__name__)
config_class = "DevConfig"
app.config.from_object(f"config.{config_class}")
db.init_app(app)
initialize_models()

app.register_blueprint(auth_routes)
app.register_blueprint(menu_routes)
app.register_blueprint(user_routes)
app.register_blueprint(admin_routes)

if __name__ == "__main__":
    try:
        app.run(debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
