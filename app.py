# Các thư viện
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime

# Hàm hiển thị thời gian
from relative_date import display_time
# Khởi tạo app
from settings import app, db, login_manager
# Các models của database
from models import Post, User, Comment, LikedComment, LikedPost
# Các Form
from form import NewPostForm, SignUpForm, LoginForm, CommentForm


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/get-all-posts')
def get_all_posts():
    """
    Nếu hiển thị hết post (page == 0)
        Hiển thị đã hết post
    Sắp xếp giảm dần tất cả post. Phân trang mỗi trang 5 post \n
    Trả về 5 post theo số page
    """
    page = request.args.get('page', type=int)
    if page == 0:
        return render_template('post-card.html', posts=None, display_time=display_time, now=datetime.now())
    posts = Post.query.order_by(desc(Post.id)).paginate(page=page, per_page=5)
    return render_template("post-card.html", posts=posts, display_time=display_time, now=datetime.now())


@app.route('/like-post', methods=["GET"])
@login_required
def like_post():
    """
    Để truy cập route này cần phải đăng nhập \n
    Lấy id của post và id của người dùng hiện tại. \n
    Nếu người dùng đã like post:
        Bỏ like post
    Ngược lại:
        Like post
    """
    post_id = int(request.args.get('id'))
    if current_user.has_liked_post(post_id):
        current_user.unlike_post(post_id)
        db.session.commit()
    else:
        current_user.like_post(post_id)
        db.session.commit()
    return ''


@app.route('/new-post', methods=['GET', "POST"])
@login_required
def new_post():
    """
    Method == GET:
        Hiển thị form đăng post mới.
    Method == POST:
        Xác nhận form
            Tạo obj Post mới rồi add vô database.
    """
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
    """
    Method == GET:
        Hiển thị form đăng ký.
    Method == POST:
        Xác nhận form, nếu thỏa thì tạo obj User mới rồi add vô database.
        Đăng nhập user vừa tạo.
    """
    form = SignUpForm()
    if form.validate_on_submit():
        salt = generate_password_hash(form.password.data, 'pbkdf2:sha256', salt_length=8)
        new_user = User(name=form.name.data, email=form.email.data, password=salt)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('sign-up.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Method == GET:
        Hiển thị form đăng nhập.
    Method == POST:
        Xác nhận form:
            Tìm user có email vừa nhập trong database.
                Nếu không tìm thấy, hiển thị lỗi và Hiển thị lại form đăng nhập.
            Kiểm tra password:
                Nếu sai cũng hiển thị lỗi và Hiển thị lại form đăng nhập.
            Nếu tất cả đều thỏa thì đăng nhập người dùng.
    """
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
    """
    Đăng xuất người dùng hiện tại
    """
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def get_post(post_id):
    """
    :param post_id: id của post cần xem.
    :return: render post.
    """
    post = Post.query.get(post_id)
    form = CommentForm()
    return render_template('post.html', post=post, display_time=display_time, form=form)


@app.route("/send-comment/<int:post_id>", methods=['POST'])
@login_required
def send_comment(post_id):
    """
    Nếu form đã xác nhận:
        Tạo obj Comment mới rồi add vô database.
        Reset lại form.content bằng chuỗi rỗng.
    :param post_id: id của post cần comment.
    :return: render phần comments
    """
    form = CommentForm()
    post = Post.query.get(post_id)
    if form.validate_on_submit():
        now = datetime.now()
        new_comment = Comment(date=now, content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        form.content.data = ""
        return render_template('send-comment.html', form=form, post=post, display_time=display_time)
    return render_template('send-comment.html', form=form, post=post, display_time=display_time)


@app.route('/like-comment', methods=["GET"])
@login_required
def like_comment():
    """
        Để truy cập route này cần phải đăng nhập \n
        Lấy id của comment và id của người dùng hiện tại. \n
        Nếu người dùng đã like comment:
            Bỏ like comment
        Ngược lại:
            Like comment
    """
    comment_id = int(request.args.get('id'))
    if current_user.has_liked_comment(comment_id):
        current_user.unlike_comment(comment_id)
        db.session.commit()
    else:
        current_user.like_comment(comment_id)
        db.session.commit()
    return ''


@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    likes_of_post = LikedPost.query.filter_by(post_id=post_id)
    for like in likes_of_post:
        db.session.delete(like)

    comments_of_post = Comment.query.filter_by(post_id=post_id)

    for comment in comments_of_post:
        likes_of_comment = LikedComment.query.filter_by(comment_id=comment.id)
        for like in likes_of_comment:
            db.session.delete(like)
        db.session.delete(comment)

    post_delete = Post.query.get(post_id)
    db.session.delete(post_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
