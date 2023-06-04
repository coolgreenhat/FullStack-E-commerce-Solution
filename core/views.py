from flask import Blueprint, redirect, render_template, flash, url_for, request, session
from core.models import Product, User, Cart, User_Roles, Order, OrderItems
from .forms import AddToCartForm, CreateProductForm, AssignUserRoleForm, DeleteFromCartForm, EmptyCartForm, ConfirmPaymentForm
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


@views.route('profile/<username>/edit', methods=['GET','PUT'])
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
# @views.route('/<userId>/orders',methods=['GET'])
# @login_required
# def orders_page(**args):
#     orders = Order.query.filter(**args).all()
#     return render_template('orders.html', orders=orders)

### Cart
@views.route('/cart',methods=['GET'])
@login_required
def cart_page():
    current_user_cart = []
    session['current_user_cart'] = []
    empty_cart_form = EmptyCartForm()
    delete_from_cart_form = DeleteFromCartForm()
    # Fetch Carts and Products data
    data = db.session.query(Cart,Product).filter(Cart.user_id==current_user.id).join(Product).all()
    # for d in data:
    #     if d["Cart"].user_id == current_user.id:
    #         current_user_cart.append(d)
    #         session['current_user_cart'].append()
    session['current_user_cart'] = [d["Cart"].id for d in data]
    payment_amount = 0
    for cart_item_id in session['current_user_cart']:
        cart_item = Cart.query.get(cart_item_id)
        payment_amount += cart_item.desired_quantity * cart_item.unit_price
    # session['']
    return render_template('cart.html', data=data, 
    delete_from_cart_form=delete_from_cart_form, 
    empty_cart_form=empty_cart_form,payment_amount=payment_amount)

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
    cart_item = Cart.query.filter_by(product_id=productId, user_id=current_user.id).first()
    db.session.delete(cart_item)
    db.session.commit()
    flash(f'Your Cart has been Cleared', category="success")
    return redirect(url_for('views.cart_page'))

@views.route('/confirm/payment', methods=['POST'])
@login_required
def confirm_payment(**args):
    order = Order(user_id=current_user.id,
            total_price=session['total_amount'],
            address=request.form.get('shipping_address'),
            payment_method=request.form.get('payment_method'),
            money_received=session['total_amount']
            )
    db.session.add(order)
    db.session.commit()
    db.session.flush()
    db.session.refresh(order)
    for item in session['current_user_cart']:
        cart_item = Cart.query.get(item)
        order_item = OrderItems(order_id=order.id,
                                product_id=cart_item.product_id,
                                quantity=cart_item.desired_quantity,
                                unit_price=cart_item.unit_price,
                                )
        db.session.add(order_item)
        db.session.commit()
    clear_cart()
    session['current_user_cart'] = []
    session['payment_succeeded'] = True
    return render_template('payment_confirmation.html', total_amount=session['total_amount'])

def clear_cart():
    for cart_id in session['current_user_cart']:
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

@views.route('/empty-cart', methods=['POST'])
@login_required
def empty_cart(**args):
    clear_cart()
    return redirect(url_for('views.cart_page'))

@views.route('/increment/<productId>', methods=["POST"])
@login_required
def increment_quantity(**args):
    """
    Increase Product Quantity from Cart Page.
    """
    productId= args['productId']
    product = Product.query.get(productId)
    existing_item = Cart.query.filter_by(product_id=product.id, user_id=current_user.id).first()
    existing_item.desired_quantity += 1
    # cart = Cart(product_id=productId, user_id=current_user.id, 
        # unit_price=product.unit_price)
    db.session.add(existing_item)
    db.session.commit()
    return redirect(url_for('views.cart_page'))


@views.route('/decrement/<productId>', methods=["POST"])
@login_required
def decrement_quantity(**args):
    """
    Decrease Product Quantity from Cart Page.
    """
    productId= args['productId']
    product = Product.query.get(productId)
    existing_item = Cart.query.filter_by(product_id=product.id,user_id=current_user.id).first()
    existing_item.desired_quantity -= 1
    if existing_item.desired_quantity == 0:
        delete_from_cart(**args)
    else:
    # cart = Cart(product_id=productId, user_id=current_user.id,
        # unit_price=product.unit_price)
        db.session.add(existing_item)
        db.session.commit()
    return redirect(url_for('views.cart_page'))

@views.route('checkout', methods=['GET'])
@login_required
def checkout_page():
    confirm_payment_form = ConfirmPaymentForm()
    payment_amount = 0
    for cart_item_id in session['current_user_cart']:
        cart_item = Cart.query.get(cart_item_id)
        payment_amount += cart_item.desired_quantity * cart_item.unit_price
    session['total_amount'] = payment_amount
    confirm_payment_form.payment_amount = payment_amount
    PAYMENT_METHODS = ['Cash On Delivery', 'Visa', 'MasterCard','UPI']
    return render_template('checkout_page.html', confirm_payment_form=confirm_payment_form)

@views.route('change/visibility', methods=['POST'])
@login_required
def product_visibility(**args):
    productId= args['productId']
    product = Product.query.get(productId)
    product = product.v
    db.session.add(product)
    db.session.commit()
    products = Product.query.all()
    return render_template('inventory.html',products=products)

