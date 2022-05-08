from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from datetime import datetime
from relative_date import display_time
from flask_ckeditor import CKEditor
import requests
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///post.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

csrf = CSRFProtect(app)
boostrap = Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)
# My module
from models import Post, User, Comment
from form import NewPostForm, SignUpForm, LoginForm, CommentForm


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():  # put application's code here
    return render_template("home.html")


@app.route('/index')
def index():
    page = request.args.get('page', type=int)
    if page == 0:
        return render_template('post-card.html', posts=None, display_time=display_time, now=datetime.now())
    posts = Post.query.order_by(desc(Post.id)).paginate(page=page, per_page=5)
    return render_template("post-card.html", posts=posts, display_time=display_time, now=datetime.now())


@app.route('/like-post', methods=["GET"])
@login_required
def like_post():
    post_id = int(request.args.get('id'))
    action = request.args.get('action')
    if action == 'like':
        current_user.like_post(post_id)
        db.session.commit()
    if action == 'unliked':
        current_user.unlike_post(post_id)
        db.session.commit()
    return ''


@app.route('/new-post', methods=['GET', "POST"])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        today = datetime.now()
        title = form.title.data
        content = form.content.data
        new_post_obj = Post(title=title, content=content, user_id=current_user.get_id(), date=today)
        db.session.add(new_post_obj)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new-post.html', form=form)


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        salt = generate_password_hash(form.password.data, 'pbkdf2:sha256')
        new_user = User(name=form.name.data, email=form.email.data, password=salt)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('sign-up.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Email doesn't exit.")
            return render_template('login.html', form=form)
        if not check_password_hash(user.password, form.password.data):
            flash("Password incorrect.")
            return render_template('login.html', form=form)
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def get_post(post_id):
    post = Post.query.get(post_id)
    form = CommentForm()
    return render_template('post.html', post=post, display_time=display_time, form=form)


@app.route("/send-comment/<int:post_id>", methods=['POST'])
@login_required
def send_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        now = datetime.now()
        new_comment = Comment(date=now, content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('get_post', post_id=post_id))
    return redirect(url_for('get_post', post_id=post_id))


@app.route('/like-comment', methods=["GET"])
@login_required
def like_comment():
    comment_id = int(request.args.get('id'))
    action = request.args.get('action')
    if action == 'like':
        current_user.like_comment(comment_id)
        db.session.commit()
    if action == 'unliked':
        current_user.unlike_comment(comment_id)
        db.session.commit()
    return ''

if __name__ == '__main__':
    app.run(debug=True)
