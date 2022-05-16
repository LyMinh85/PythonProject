# Các thư viện
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import desc, subquery
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import time
from flask_socketio import join_room, leave_room, send, emit
# Hàm hiển thị thời gian
from relative_date import display_time
# Khởi tạo app
from settings import app, db, login_manager, UPLOAD_FOLDER, BASE_DIR, socketio
# Các models của database
from models import Post, User, Comment, LikedComment, LikedPost, Thread, ThreadParticipant, Message, MessageReadState
# Các class Form
from form import NewPostForm, SignUpForm, LoginForm, CommentForm


cloudinary.config(
    cloud_name=os.environ.get('CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.errorhandler(401)
def custom_401(error):
    return redirect(url_for('login'))


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/get-all-posts/<int:user_id>/<int:page>')
def get_all_posts(user_id, page):
    posts = None
    if page != 0:
        if user_id == 0:
            posts = Post.query.order_by(desc(Post.id)).paginate(page=page, per_page=5)
        else:
            posts = Post.query.filter_by(user_id=user_id).order_by(desc(Post.id)).paginate(page=page, per_page=5)
    return render_template("post-card.html", posts=posts, user_id=user_id, display_time=display_time)


@app.route('/like-post', methods=["GET"])
@login_required
def like_post():
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
    form = NewPostForm()
    if form.validate_on_submit():
        f = form.photo.data
        file_path = ''
        if f is not None:
            filename = secure_filename(f.filename)
            file_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, filename)
            print(file_path)
            f.save(file_path)
        today = datetime.now()
        title = form.title.data
        content = form.content.data
        new_post_obj = Post(title=title, content=content, user_id=current_user.get_id(), date=today)
        if f is not None:
            while not os.path.exists(file_path):
                time.sleep(1)
            response = cloudinary.uploader.upload(file_path,
                                                  public_id=os.urandom(4).hex(),
                                                  folder='/hiiam')
            url = response['url']
            new_post_obj.content += f"<img src='{url}' loading='lazy'/>"

        db.session.add(new_post_obj)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new-post.html', form=form)


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
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
    comment_id = int(request.args.get('id'))
    if current_user.has_liked_comment(comment_id):
        current_user.unlike_comment(comment_id)
        db.session.commit()
    else:
        current_user.like_comment(comment_id)
        db.session.commit()
    return ''


@app.route("/delete-post/<int:post_id>")
@login_required
def delete_post(post_id):
    post_delete = Post.query.get(post_id)

    if current_user.id != post_delete.user.id:
        return redirect(url_for('home'))

    likes_of_post = LikedPost.query.filter_by(post_id=post_id)
    for like in likes_of_post:
        db.session.delete(like)

    comments_of_post = Comment.query.filter_by(post_id=post_id)

    for comment in comments_of_post:
        likes_of_comment = LikedComment.query.filter_by(comment_id=comment.id)
        for like in likes_of_comment:
            db.session.delete(like)
        db.session.delete(comment)

    db.session.delete(post_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/user/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get(user_id)

    count_liked = 0
    for post in user.posts:
        count_liked += post.post_likes.count()

    return render_template('profile.html', user=user, count_liked=count_liked)


@app.route('/create-new-thread/<int:user_id>', methods=['GET'])
@login_required
def create_new_thread(user_id):
    thread_current_user = ThreadParticipant.query.filter_by(user_id=current_user.id)
    sq = ThreadParticipant.query.filter_by(user_id=user_id).subquery()
    result = thread_current_user.join(sq, ThreadParticipant.thread_id == sq.c.thread_id).first()
    if result:
        return redirect(url_for('chat_page'))
    new_thread = Thread()
    db.session.add(new_thread)
    db.session.flush()
    new_participant_1 = ThreadParticipant(thread_id=new_thread.id, user_id=current_user.id)
    new_participant_2 = ThreadParticipant(thread_id=new_thread.id, user_id=user_id)
    db.session.add(new_participant_1)
    db.session.add(new_participant_2)
    db.session.commit()
    return redirect(url_for('chat_page'))


@app.route('/chat')
@login_required
def chat_page():
    thread_id = request.args.get('thread_id')
    threads = Thread.query.join(Thread.participants).filter_by(user_id=current_user.id)
    chat_thread_html = None
    thread = None
    if thread_id:
        thread = Thread.query.get(thread_id)
        user = None
        for participant in thread.participants:
            if participant.user.id != current_user.id:
                user = participant.user
        messages = thread.thread_messages.order_by(desc(Message.id)).paginate(page=1, per_page=10)
        chat_thread_html = render_template('chat-thread.html',
                                           thread=thread,
                                           messages=messages,
                                           user=user,
                                           reversed=reversed)
    list_thread_template = render_template('list-thread.html',
                                           threads=threads,
                                           Message=Message,
                                           desc=desc,
                                           current_thread=thread)
    return render_template('chat.html',
                           list_thread_template=list_thread_template,
                           chat_thread_html=chat_thread_html,
                           thread=thread
                           )


@socketio.on('send-message')
@login_required
def handle_my_custom_event(data, methods=['GET', 'POST']):
    user_send = User.query.get(int(data['user_id']))
    new_message = Message(
        thread_id=data['thread_id'],
        send_date=datetime.now(),
        sending_user_id=data['user_id'],
        body=data['message']
    )
    db.session.add(new_message)
    db.session.commit()
    json_response = {
        'user_id': user_send.id,
        'html': render_template(
            'message.html',
            user_send=user_send,
            message=data['message'],
            send_date=datetime.now()
        ),
        'send_date': datetime.now().strftime('%d/%m/%Y, %I:%M %p'),
        'token': data['token'],
    }
    emit('received-message', json_response, room=data['thread_id'])


@socketio.on('join')
@login_required
def on_join(data):
    room = data['room']
    join_room(room)
    send(f"Join", room=room)


@socketio.on('leave')
@login_required
def on_leave(data):
    room = data['room']
    leave_room(room)
    send(f"Leave", room=room)


if __name__ == '__main__':
    app.run(debug=True)
