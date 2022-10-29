import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
DB_NAME = os.environ.get("DB_NAME")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_NAME
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #bootswatch theme
    app.config['FLASK_ADMIN_SWATCH'] = "cerulean"
    db.init_app(app)

    admin = Admin(app, name="Shop")

    bootstrap = Bootstrap(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(views, url_prefix="/")

    from .models import Product, User, Cart, User_Roles, Order, OrderItems, Ratings, Roles
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Product, db.session))
    admin.add_view(ModelView(Cart, db.session))
    admin.add_view(ModelView(User_Roles, db.session))
    admin.add_view(ModelView(Roles, db.session))
    admin.add_view(ModelView(Order, db.session))
    admin.add_view(ModelView(OrderItems, db.session))
    admin.add_view(ModelView(Ratings, db.session))

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # @app.after_request
    # def add_header(response):
        # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
   
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/'+ DB_NAME):
        db.create_all(app=app)
        print("Database Created!")


