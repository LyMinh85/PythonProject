from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_minify import Minify
from flask_socketio import SocketIO
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'static/photos/'


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///post.db')
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
boostrap = Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
Minify(app=app, html=True, js=True, cssless=True)

db = SQLAlchemy(app)





