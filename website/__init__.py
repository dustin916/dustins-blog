from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor
import os
from os import path


db = SQLAlchemy()
DB_NAME = 'database.db'

ckeditor = CKEditor()

UPLOAD_IMAGE_FOLDER = 'website\static\images'
UPLOAD_PROFILE_PIC_FOLDER = 'website\static\images\profile_pic'
UPLOAD_AUDIO_FOLDER = 'website\static\sermon'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['DustinsBlogSecretKey']
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
    app.config['UPLOAD_PROFILE_PIC_FOLDER'] = UPLOAD_PROFILE_PIC_FOLDER
    app.config['UPLOAD_AUDIO_FOLDER'] = UPLOAD_AUDIO_FOLDER
    app.config['CKEDITOR_PKG_TYPE'] = 'full'  # basic, standard or full
    app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ldtuz0mAAAAABhn9RElj51ar-X3Y99DQCCexqw_'
    app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ldtuz0mAAAAAHxj7bFjkgOZuarmNyj5Z077GbAY'

    ckeditor.init_app(app)

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Subscribers, Sermons, Blog, Pic, Admin, AboutMe, ProfilePic
    Subscribers()
    Sermons()
    Blog()
    Pic()
    Admin()
    AboutMe()
    ProfilePic()

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.dash_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Admin.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

