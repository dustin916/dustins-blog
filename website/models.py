from website import db
from sqlalchemy.sql import func
from datetime import datetime, timezone
from flask_login import UserMixin


class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=func.now())

    # Create a  function to return a string when we add something to the database
    def __repr__(self):
        return '<Name  %r>' % self.id


class Sermons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Pic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pic = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now())


class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    welcome = db.Column(db.String(500), nullable=False)
    about = db.Column(db.Text)


class ProfilePic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_pic = db.Column(db.String(500), nullable=False)


# admin user only
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))
