from flask import Blueprint, render_template, request, flash, redirect,url_for, session
from core.forms import LoginForm, RegistrationForm
from .models import User
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from email_validator import validate_email,EmailNotValidError

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method  == 'POST':
        password = request.form.get('password')
        login_string = request.form.get('email')
        user = None
        user = User.query.filter_by(username=login_string).first()
        if user is None:
            user = User.query.filter_by(email=login_string).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category="success")
                login_user(user, remember=True)
                return redirect(url_for('views.home_page'))
            else:
                flash('Incorrect password, try again.', category="error")
        else:
            flash('User Does not exist.', category='error')
    return render_template("login.html", user=current_user, form=form)

@login_required
@auth.route('/logout')
def logout():
    #session.clear()
    logout_user()
    flash('You are logged Out.', category="success")
    return redirect(url_for('auth.login'))

@auth.route('/register',methods=['GET', 'POST'])
def signup():
    session = {}
    form = RegistrationForm()
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password1 = request.form.get('password')
            password2 = request.form.get('password2')
            session['username'] = username
            session['password1'] = password1
            session['password2'] = password2
            emailid = request.form.get('email')
            session['emailid'] = emailid
            email = validate_email(emailid).email
        except EmailNotValidError as e:
            flash(str(e), category="warning")
            return render_template("register.html", form=form, session=session)

        user = User.query.filter_by(username=username,email=email).first()

        if user:
            flash("User with that email or username already exists.", category="warning")
        elif len(email) < 8:
            flash('Enter a valid email', category="warning")
        elif len(username) < 2:
            flash('Not a valid username', category="warning")
        elif password1 != password2:
            flash('Passwords don\'t match', category="warning")
        elif len(password1) < 8:
            flash('Passwords too short', category="warning")
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            # login_user(new_user, remember=True)
            flash('Account Created. Please Login to continue', category="success")
            return redirect(url_for('auth.login'))
    return render_template("register.html", form=form, session=session)
