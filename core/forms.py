from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email , EqualTo, Regexp, NumberRange
from wtforms import ValidationError
from core.models import User

class LoginForm(FlaskForm):
    email = StringField('Email or Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    remember_me = BooleanField('By Signing-in up I accept terms and conditions.')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity',default=1,validators=[DataRequired()])
    submit = SubmitField('Add To Cart')

class DeleteFromCartFrom(FlaskForm):
    quantity = IntegerField('Quantity',default=1,validators=[DataRequired()])
    submit = SubmitField('Remove From Cart')

class CreateProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Product Description', validators=[DataRequired(), Length(1, 255)])
    category = StringField('Product Category', validators=[DataRequired(), Length(1, 50)])
    stock = IntegerField('Stock',validators=[DataRequired()])
    unit_price = IntegerField('Price Per Unit',validators=[DataRequired()])
    visibility = BooleanField('Visible to Customer')
    submit = SubmitField('Create Product')

class AssignUserRoleForm(FlaskForm):
    user = StringField('Username', validators=[DataRequired()])
    role = StringField('Role',validators=[DataRequired()])
    is_active = BooleanField('Is Active')
