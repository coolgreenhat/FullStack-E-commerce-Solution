from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from hashlib import md5

class Products(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=50), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    category = db.Column(db.String(length=30), nullable=False)
    stock = db.Column(db.Integer(),nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
    unit_price = db.Column(db.Integer(), nullable=False)
    visibility = db.Column(db.Boolean, default=True, nullable=False)
    average_rating = db.Column(db.Integer(), nullable=False, default=0)
    order_items = db.relationship('OrderItems', backref='order_items',lazy=True)  # Many To One Relationship
    cart = db.relationship('Cart', backref='cart',lazy=True)  # Many To One Relationship
    ratings = db.relationship('Ratings', backref='ratings',lazy=True)  # Many To Many Relationship

    def __repr__(self) -> str:
        return f'{self.name}'

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(60))
    username = db.Column(db.String(15))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    user_roles = db.relationship('User_Roles', backref='user_role',lazy=True)
    orders = db.relationship('Orders', backref='user_orders',lazy=True) # One To Many Relationship
    cart = db.relationship('Cart', backref='user_cart',lazy=True) # One To Many Relationship
    ratings = db.relationship('Ratings', backref='user_ratings',lazy=True) # One To Many Relationship

    def __repr__(self) -> str:
        return f'{self.username}'

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Roles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
    user_roles = db.relationship('User_Roles', backref='role_user',lazy=True)  # One To Many Relationship

class User_Roles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Users
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id')) # Foreign Key : Roles
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())

class Orders(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Users
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    total_price = db.Column(db.Integer(),nullable=False)
    address = db.Column(db.Integer(),nullable=False)
    payment_method = db.Column(db.String(length=30))
    money_received = db.Column(db.Integer(), nullable=False)
    order_items = db.relationship('OrderItems', backref='order_orderitems',lazy=True)  # One To Many Relationship

class OrderItems(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    order_id = db.Column(db.Integer(), db.ForeignKey('orders.id')) # Foreign Key : Orders
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id')) # Foreign Key : Products
    quantity = db.Column(db.Integer(),nullable=False)
    unit_price = db.Column(db.Integer(), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id')) # Foreign Key : Products
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Cart
    desired_quantity = db.Column(db.Integer(),nullable=False)
    unit_price = db.Column(db.Integer(),nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())

class Ratings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), db.ForeignKey('products.id')) # Foreign Key : Product
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id')) # Foreign Key : Users
    rating = db.Column(db.Integer(),nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    modified = db.Column(db.DateTime(timezone=True), default=func.now())
