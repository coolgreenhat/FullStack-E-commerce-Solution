from flask import Blueprint, redirect, render_template, flash, url_for, request
from core.models import Product, User, Cart, User_Roles
from .forms import AddToCartForm, CreateProductForm, AssignUserRoleForm, DeleteFromCartFrom
from flask_login import login_required, current_user, fresh_login_required
from .permissions import admin_login_required, staff_login_required
from . import db

views = Blueprint('views', __name__)

@views.route('/',methods=['GET'])
@fresh_login_required
@login_required
def home_page():
    add_to_cart_form = AddToCartForm()
    products = Product.query.all()
    return render_template('index.html',products=products, add_to_cart_form=add_to_cart_form)

# Profile
@views.route('profile/<username>',methods=['GET'])
@login_required
def profile_page(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html',user=user)


@views.route('profile/edit/<username>', methods=['GET','PUT'])
@login_required
def edit_profile_page(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html',user=user)

# Inventory
@views.route('/inventory',methods=['GET'])
@login_required
def inventory_page():
    products = Product.query.all()
    return render_template('inventory.html',products=products)


# Orders
@views.route('/<userId>/orders',methods=['GET'])
@login_required
def orders_page(**args):
    orders = Order.query.filter(**args).all()
    return render_template('orders.html', orders=orders)


### Cart
@views.route('/cart',methods=['GET'])
@login_required
def cart_page():
    delete_from_cart_form = DeleteFromCartFrom()
    data = db.session.query(Cart,Product).join(Product).all()
    return render_template('cart.html', data=data, delete_from_cart_form=delete_from_cart_form)

@views.route('/add-to-cart/<productId>', methods=['GET','POST'])
@login_required
def add_to_cart(**args):
    desired_quantity = int(request.form.get('quantity'))
    productId= args['productId']
    product = Product.query.get(productId)
    existing_item = None
    try:
        existing_item = Cart.query.filter_by(product_id=product.id,user_id=current_user.id).first()
    except Exception:
        pass
    if existing_item is not None:
        existing_item.desired_quantity += desired_quantity
    else:
        cart = Cart(product_id=productId,
        user_id=current_user.id,
        desired_quantity=desired_quantity,
        unit_price=product.unit_price)
        db.session.add(cart)
    db.session.commit()
    flash(f'{desired_quantity} {product.name} Added to Cart', category="success")
    return redirect(url_for('views.home_page'))

@views.route('/remove-from-cart/<productId>', methods=['POST'])
@login_required
def delete_from_cart(**args):
    productId= args['productId']
    cart = Cart.query.get(productId)
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('views.cart_page'))

@views.route('/increment/<productId>', methods=["POST"])
def increment_quantity(**args):
    """
    Increase Product Quantity from Cart Page.
    """
    productId= args['productId']
    product = Product.query.get(productId)
    existing_item = Cart.query.filter_by(product_id=product.id,user_id=current_user.id).first()
    existing_item.desired_quantity += 1
    cart = Cart(product_id=productId, user_id=current_user.id,
        unit_price=product.unit_price)
    db.session.add(cart)
    db.session.commit()
    return redirect(url_for('views.cart_page'))
