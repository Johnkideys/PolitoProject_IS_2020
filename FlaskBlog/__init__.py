from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'jdnrewbhgvjxgxgnrxebx'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site1.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from FlaskBlog import routes

"""
from flask_uploads import UploadSet
from flask_uploads import configure_uploads
from flask_uploads import IMAGES, patch_request_class


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()+"/static"
"""