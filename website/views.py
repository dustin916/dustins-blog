from flask import Flask, Blueprint, render_template, request, url_for
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email

from email_validator import validate_email
from itsdangerous import URLSafeSerializer

import smtplib
import os

from .models import Subscribers, Sermons, Blog, Pic, AboutMe, ProfilePic
from . import db
from sqlalchemy.exc import IntegrityError
from smtplib import SMTPRecipientsRefused


dustin_email = "dustinsblog22@gmail.com"
dustin_pw = os.environ['WEB_BLG_APP_PW']

s = URLSafeSerializer(os.environ['DustinsBlogUnsubscribeSecretKey'])


class SubscribeForm(FlaskForm):
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired(), Email(message="Please enter a valid email.")])
    # email variable still doesn't validate the email
    submit = SubmitField("Submit")


class ContactForm(FlaskForm):
    subject = SelectField(choices=['Bible', 'Spiritual Things', 'Website', 'Just to Talk', 'Other'])
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
    text = TextAreaField(validators=[DataRequired(), Email(message="Please enter a valid email.")])
    # text variable still doesn't validate the email
    submit = SubmitField("Submit")


views = Blueprint('views', __name__)


@views.route('/')
def about_me():
    title = "About Me"
    aboutme = AboutMe.query.order_by(AboutMe.id)
    profilepic = ProfilePic.query.order_by(ProfilePic.id)
    return render_template('about_me.html', title=title, aboutme=aboutme, profilepic=profilepic)


@views.route('/blog')
def blog():
    title = "Blog"
    blog_list = Blog.query.order_by(desc(Blog.id))
    return render_template('blog.html', title=title, blog_list=blog_list)


@views.route('/blog/<int:id>')
def individual_blog(id):
    blog = Blog.query.get_or_404(id)
    return render_template('individual_blog.html', blog=blog)


@views.route('/images')
def images():
    title = "Images"
    image_list = Pic.query.order_by(desc(Pic.id))
    return render_template('images.html', title=title, image_list=image_list)


@views.route('/images/<int:id>')
def individual_image(id):
    image = Pic.query.get_or_404(id)
    return render_template('individual_image.html', image=image)


@views.route('/sermons')
def sermons():  # audio files
    title = "Sermons"
    sermon_list = Sermons.query.order_by(desc(Sermons.id))
    return render_template('sermons.html', title=title, sermon_list=sermon_list)


@views.route('/sermons/<int:id>')
def sermon(id):
    sermon = Sermons.query.get_or_404(id)
    sermon_list = Sermons.query.order_by(desc(Sermons.id))
    return render_template('sermon.html', sermon=sermon, sermon_list=sermon_list)


@views.route('/contact', methods=['POST', 'GET'])
def subscribe_contact():  # rev.dustinoliver@gmail.com
    title = "Subscribe/Contact"
    subject = 'Bible'
    first_name = None
    last_name = None
    email = None
    text = None
    subscribe = SubscribeForm()
    contact = ContactForm()
    # Validate Forms
    if subscribe.validate_on_submit():
        first_name = subscribe.first_name.data
        subscribe.first_name.data = ''
        last_name = subscribe.last_name.data
        subscribe.last_name.data = ''
        email = subscribe.email.data
        is_valid = validate_email(email, verify=True)
        if is_valid:
            subscribe.email.data = ''
            return render_template('subscribe_contact.html', title=title, first_name=first_name, last_name=last_name,
                                   email=email, text=text, subject=subject, subscribe=subscribe, contact=contact)
            
        else:
            print('Please use a valid email.')

    elif contact.validate_on_submit():
        subject = contact.subject.data
        first_name = contact.first_name.data
        contact.first_name.data = ''
        last_name = contact.last_name.data
        contact.last_name.data = ''
        email = contact.email.data
        contact.email.data = ''
        text = contact.text.data
        contact.text.data = ''
    return render_template('subscribe_contact.html', title=title, first_name=first_name, last_name=last_name,
                           email=email, text=text, subject=subject, subscribe=subscribe, contact=contact)


@views.route('/thank-you', methods=['POST'])
def thank_you():
    subject = request.form.get("subject")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    message = request.form.get("text")

    response_message = "Thank you for contacting me."
    message_to_me = ("name: " + first_name + " " + last_name) + ("\nemail: " + email) + ("\nmessage: " + message)
    email_to_me = 'Subject: {}\n\n{}'.format(subject, message_to_me)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(dustin_email, dustin_pw)
    server.sendmail(dustin_email, email, response_message)
    server.sendmail(dustin_email,
                    dustin_email, email_to_me)

    title = "Thank You"
    return render_template('thank_you.html', title=title, subject=subject, first_name=first_name, last_name=last_name,
                           email=email, message=message)


@views.route('/subscriber-thank-you', methods=['GET', 'POST'])
def subscriber_thank_you():
    title = "Subscriber Thank You"
    if request.method == 'GET' or 'POST':
        subscriber_first_name = request.form.get("first_name")
        subscriber_last_name = request.form.get("last_name")
        subscriber_email = request.form.get("email")
        
        subscribers = Subscribers.query.order_by(Subscribers.id)

        # Add to database
        new_subscriber = Subscribers(first_name=subscriber_first_name, last_name=subscriber_last_name,
                                     email=subscriber_email)
    
        # Push to database
        
        try:
            db.session.add(new_subscriber)
            db.session.commit()

            token = s.dumps(subscriber_email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")

            new_subscriber_message = "You have a new subscriber!"
            subscriber_message = """
Thank you. You have been subscribed. 




If you wish to be removed from the subscription please click the link below:
{} 
            """.format(link)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)

            server.sendmail(dustin_email,
                            subscriber_email, subscriber_message)
            server.sendmail(dustin_email, dustin_email, new_subscriber_message + "\n" + subscriber_first_name + " " +
                            subscriber_last_name + "\n" + subscriber_email)

            return render_template('subscriber_thank_you.html', title=title, subscribers=subscribers,
                                   new_subscriber=new_subscriber)
        except IntegrityError:
            db.session.rollback()
            return "<h1>The email you used already exists.</h1>"
        except SMTPRecipientsRefused:
            db.session.rollback()
            return "<h1>The email address you entered is not valid.</h1>"


@views.route('/unsubscribe/<token>')
def unsubscribe(token):
    try:
        subscriber_email = s.loads(token, salt='unsubscribe')
        subscriber_to_delete = Subscribers.query.filter_by(email=subscriber_email).first()
        if subscriber_to_delete:
            db.session.delete(subscriber_to_delete)
            db.session.commit()    
    except:
        return '<h1>I am sorry, an error occurred. Please let me know about this.</h1>'
    return render_template('unsubscribe.html')


# Custom Error Pages -------------------

# Invalid URL
@views.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal Server Error
@views.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
