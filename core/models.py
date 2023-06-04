from . import db

from sqlalchemy.sql import func
from sqlalchemy.orm import backref, relationship
from flask_login import UserMixin
from hashlib import md5

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id')) # Foreign Key : Products
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Cart
    desired_quantity = db.Column(db.Integer(),nullable=False)
    unit_price = db.Column(db.Integer(),nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
    products = db.relationship("Product", back_populates="carts", lazy="select")
    users = db.relationship("User",back_populates="carts", lazy="select")
    __table_args__ = (db.UniqueConstraint('product_id','user_id',name="__product_user_uc"),)

    def __repr__(self) -> str:
        return f'{self.id}'

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer(), primary_key=True)
    image_url = db.Column(db.String(),nullable=False,unique=True)
    name = db.Column(db.String(length=50), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    category = db.Column(db.String(length=30), nullable=False)
    stock = db.Column(db.Integer(),nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
    unit_price = db.Column(db.Integer(), nullable=False)
    visibility = db.Column(db.Boolean, default=True, nullable=False)
    carts = db.relationship("Cart", back_populates="products", lazy="select")

    def __repr__(self) -> str:
        return f'{self.name}'

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(60))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(15))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    user_roles = db.relationship('User_Roles',back_populates='users',lazy="select")
    carts = db.relationship('Cart', back_populates='users',lazy="select")

    def __repr__(self) -> str:
        return f'{self.username}'

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
    user_roles = db.relationship('User_Roles',back_populates='roles',lazy="select")

    def __repr__(self) -> str:
        return f'{self.name}'

class User_Roles(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(),db.ForeignKey("users.id"))
    users = relationship('User',back_populates="user_roles",lazy="select")
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id')) # Foreign Key : Roles
    roles = relationship('Roles', back_populates="user_roles",lazy="select")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())

    def __repr__(self) -> str:
        return f'{self.roles.name}'

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Users
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    total_price = db.Column(db.Integer(),nullable=False)
    address = db.Column(db.Text(),nullable=False)
    payment_method = db.Column(db.String(length=30))
    money_received = db.Column(db.Integer(), nullable=False)

class OrderItems(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id')) # Foreign Key : Orders
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id')) # Foreign Key : Products
    quantity = db.Column(db.Integer(),nullable=False)
    unit_price = db.Column(db.Integer(), nullable=False)
    orders = db.relationship("Order", backref="order_items", lazy="select")
    products = db.relationship("Product", backref="order_items", lazy="select")

class Ratings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id')) # Foreign Key : Product
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Users
    rating = db.Column(db.Integer(),nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
    products = db.relationship("Product", backref="rating_product", lazy="select")
    users = db.relationship("User", backref="rating_user", lazy="select")

