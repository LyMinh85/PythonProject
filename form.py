from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']


class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    photo = FileField('Image', validators=[FileRequired(),
                                           FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])
    submit = SubmitField('Post')


class SignUpForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    email = EmailField('Your Email', validators=[Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Your Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField("Your Email", validators=[DataRequired(), Email()])
    password = PasswordField("Your Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    content = TextAreaField("Write comment", validators=[DataRequired()])
    submit = SubmitField("Send")