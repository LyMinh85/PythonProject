from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
import random
from flask_gravatar import Gravatar
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)


db.create_all()


# response = requests.get('https://zenquotes.io/?api=quotes')
# quotes = response.json()
# for quote in quotes:
#     new_post = Post(content=quote['q'], author=quote['a'])
#     db.session.add(new_post)
#
# db.session.commit()

@app.route('/')
def home():  # put application's code here
    posts = Post.query.paginate(page=1, per_page=5)
    return render_template("home.html", posts=posts)


@app.route('/index')
def index():
    page = request.args.get('page', type=int)
    random_minutes = [random.randint(1,59) for i in range(5)]
    if page == 0:
        return render_template('card-post.html', posts=None, random_minutes=random_minutes)
    posts = Post.query.paginate(page=page, per_page=5)
    return render_template("card-post.html", posts=posts, random_minutes=random_minutes)


@app.route('/post')
def post():
    return render_template("card-post.html")


if __name__ == '__main__':
    app.run(debug=True)
