from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from FlaskBlog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2,max=22)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RetailerForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators = [DataRequired()])
    picture = FileField('Update Farm Picture', validators=[FileAllowed(['png', 'jpg'])])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Post')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2,max=22)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another one.')

class UpdateProductsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    descr = TextAreaField('Description', validators = [DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class PurchaseForm(FlaskForm):
    delivery = StringField('DeliveryOption', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class CommentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators = [DataRequired()])
    submit = SubmitField('Confirm')