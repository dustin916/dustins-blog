# auth.py is only for me to access and edit content
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, current_app as app
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField
from itsdangerous import URLSafeSerializer
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import os
import json
import smtplib

from .models import Subscribers, Sermons, Blog, Pic, Admin, AboutMe, ProfilePic
from . import db


auth = Blueprint('auth', __name__)

s = URLSafeSerializer(os.environ['DustinsBlogUnsubscribeSecretKey'])
dustin_email = "dustinsblog22@gmail.com"
dustin_pw = os.environ['WEB_BLG_APP_PW']


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    caption = StringField("Caption", validators=[DataRequired()])
    submit = SubmitField("Upload File")


class UploadAudioForm(FlaskForm):
    audio_file = FileField("Audio File", validators=[DataRequired()])
    submit = SubmitField("Upload File")


class BlogForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AboutForm(FlaskForm):
    welcome = StringField("Welcome", validators=[DataRequired()])
    about = CKEditorField("About Me", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ProfPicForm(FlaskForm):
    profile_pic = FileField("Profile Picture", validators=[DataRequired()])
    submit = SubmitField("Upload File")


# routes
# ---------------------------------------------------------------------
# login/logout/sign-up


@auth.route('/dash-login', methods=['GET', 'POST'])
def dash_login():
    title = "Admin Login"
    if request.method == 'POST':
        user_name = request.form.get('username')  # set up username and password for admin
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=user_name).first()
        if admin:
            if check_password_hash(admin.password, password):
                flash('Logged in successfully! Welcome Dustin', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('auth.dash_uploader'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')
    
    return render_template('dash_login.html', title=title, user=current_user)


@auth.route('/dash-logout', methods=['GET', 'POST'])
@login_required
def dash_logout():
    logout_user()
    return redirect(url_for('auth.dash_login'))


@auth.route('/dash-sign-up', methods=['GET', 'POST'])
def dash_sign_up():
    title = "Admin Sign-up"

    if request.method == "POST":
        user_name = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        admin = Admin(username=user_name, password=generate_password_hash(password1, method='sha256'))
        db.session.add(admin)
        db.session.commit()
        login_user(admin, remember=True)
        flash('Account created! - Welcome Dustin', category='success')
        return redirect(url_for('auth.dash_uploader'))

    return render_template("dash_sign_up.html", title=title)


# Upload

@auth.route('/dash-uploader', methods=['GET', 'POST'])
@login_required
def dash_uploader():
    title = "Dash Uploader"
    aboutme = AboutMe.query.order_by(AboutMe.id)
    profilepic = ProfilePic.query.order_by(ProfilePic.id)
    blog_list = Blog.query.order_by(desc(Blog.id))
    image_list = Pic.query.order_by(desc(Pic.id))
    sermon_list = Sermons.query.order_by(desc(Sermons.id))
    subscriber_list = Subscribers.query.order_by(Subscribers.id)

    about_form = AboutForm()
    profile_pic_form = ProfPicForm()
    blog_form = BlogForm()
    image_form = UploadFileForm()
    sermon_form = UploadAudioForm()

    if about_form.validate_on_submit():
        home = AboutMe(welcome=about_form.welcome.data, about=about_form.about.data)
        # Clear the form
        about_form.welcome.data = ''
        about_form.about.data = ''
        # Add to database
        db.session.add(home)
        db.session.commit()

        # Send email to subscribers
        for subscriber in subscriber_list:
            name = subscriber.first_name + " " + subscriber.last_name
            email = subscriber.email
            token = s.dumps(email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")
            subject = "Website Update"
            mail_message = """
        Dear {}, there has been an update to my website. Please check out my new {} at www.dustinsblog.org .




        Unsubscribe:
        If you wish to be removed from the subscription please click the link below.
        {}
                """.format(name, "About Me page", link)
            message = 'Subject: {}\n\n{}'.format(subject, mail_message)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)
            server.sendmail(dustin_email, email, message)

        return render_template('dash_about_me.html', title=title, aboutme=aboutme, about_form=about_form, home=home)

    elif profile_pic_form.validate_on_submit():
        pic_file = profile_pic_form.profile_pic.data

        profile_pic_name = secure_filename(pic_file.filename)
        pic_file.save(os.path.join(app.config['UPLOAD_PROFILE_PIC_FOLDER'], profile_pic_name))
        profile_picture = ProfilePic(profile_pic=profile_pic_name)

        # Add blog to database
        db.session.add(profile_picture)
        db.session.commit()

        # Send email to subscribers
        for subscriber in subscriber_list:
            name = subscriber.first_name + " " + subscriber.last_name
            email = subscriber.email
            token = s.dumps(email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")
            subject = "Website Update"
            mail_message = """
        Dear {}, there has been an update to my website. Please check out my new {} at www.dustinsblog.org.



        Unsubscribe:
        If you wish to be removed from the subscription please click the link below.
        {}
                """.format(name, "Profile Picture", link)
            message = 'Subject: {}\n\n{}'.format(subject, mail_message)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)
            server.sendmail(dustin_email, email, message)

        return render_template('dash_about_me.html', title=title, profilepic=profilepic,
                               profile_pic_form=profile_pic_form, profile_picture=profile_picture, aboutme=aboutme)

    elif blog_form.validate_on_submit():
        blog = Blog(title=blog_form.title.data, content=blog_form.content.data)
        # Clear the Form
        blog_form.title.data = ''
        blog_form.content.data = ''
        # Add blog to database
        db.session.add(blog)
        db.session.commit()

        # send email to subscribers
        for subscriber in subscriber_list:
            name = subscriber.first_name + " " + subscriber.last_name
            email = subscriber.email
            token = s.dumps(email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")            
            subject = "Website Update"
            mail_message = """
    Dear {}, there has been an update to my website. Please check out my new {} at www.dustinsblog.org/blog.



    Unsubscribe:
    If you wish to be removed from the subscription please click the link below.
    {}
            """.format(name, "Blog", link)
            message = 'Subject: {}\n\n{}'.format(subject, mail_message)
        
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)
            server.sendmail(dustin_email, email, message)

        return render_template('dash_blog.html', title=title, blog_list=blog_list, blog_form=blog_form, blog=blog)
    
    elif image_form.validate_on_submit():
        file = image_form.file.data

        pic_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], pic_name))
        pic_blog = Pic(pic=pic_name, caption=image_form.caption.data)

        db.session.add(pic_blog)
        db.session.commit()

        # send email to subscribers
        for subscriber in subscriber_list:
            name = subscriber.first_name + " " + subscriber.last_name
            email = subscriber.email
            token = s.dumps(email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")            
            subject = "Website Update"
            mail_message = """
    Dear {}, there has been an update to my website. Please check out my new {}  at www.dustinsblog.org/images.



    Unsubscribe:
    If you wish to be removed from the subscription please click the link below.
    {}
            """.format(name, "Image", link)
            message = 'Subject: {}\n\n{}'.format(subject, mail_message)
        
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)
            server.sendmail(dustin_email, email, message)

        return render_template('dash_images.html', title=title, image_list=image_list, image_form=image_form,
                               pic_name=pic_name)
    
    elif sermon_form.validate_on_submit():
        sermon_file = sermon_form.audio_file.data

        sermon_name = secure_filename(sermon_file.filename)
        sermon_file.save(os.path.join(app.config['UPLOAD_AUDIO_FOLDER'], sermon_name))
        new_sermon = Sermons(name=sermon_name)
        
        db.session.add(new_sermon)
        db.session.commit()

        # send email to subscribers
        for subscriber in subscriber_list:
            name = subscriber.first_name + " " + subscriber.last_name
            email = subscriber.email
            token = s.dumps(email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")            
            subject = "Website Update"
            mail_message = """
    Dear {}, there has been an update to my website. Please check out my new {} at www.dustinsblog.org/sermons.



    Unsubscribe:
    If you wish to be removed from the subscription please click the link below.
    {}
            """.format(name, "Sermon", link)
            message = 'Subject: {}\n\n{}'.format(subject, mail_message)
        
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)
            server.sendmail(dustin_email, email, message)

        return render_template('dash_sermons.html', title=title, sermon_list=sermon_list, sermon_form=sermon_form)
    
    else:
        return render_template('dash_uploader.html', title=title, blog_list=blog_list, image_list=image_list,
                               image_form=image_form, sermon_form=sermon_form, blog_form=blog_form,
                               about_form=about_form, profile_pic_form=profile_pic_form)


# About Me
@auth.route('/dash-about-me', methods=['GET', 'POST'])
@login_required
def dash_about_me():
    title = "Dash About Me"
    aboutme = AboutMe.query.order_by(AboutMe.id)
    profilepic = ProfilePic.query.order_by(ProfilePic.id)
    return render_template('dash_about_me.html', title=title, aboutme=aboutme, profilepic=profilepic)


@auth.route('/dash-about-me/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def dash_about_editor(id):
    title = "Dash About Me Editor"
    about_edit = AboutMe.query.get_or_404(id)
    edit_form = AboutForm()
    subscriber_list = Subscribers.query.order_by(Subscribers.id)

    if edit_form.validate_on_submit():
        about_edit.welcome = edit_form.welcome.data
        about_edit.about = edit_form.about.data
        # Update Database
        db.session.add(about_edit)
        db.session.commit()

        # Send email to subscribers
        for subscriber in subscriber_list:
            name = subscriber.first_name + " " + subscriber.last_name
            email = subscriber.email
            token = s.dumps(email, salt='unsubscribe')
            link = url_for('views.unsubscribe', token=token, _external=True, _scheme="click here.")
            subject = "Website Update"
            mail_message = """
        Dear {}, there has been an update to my website. Please check out my updated {}.




        If you wish to be removed from the subscription please click the link below.
        {}
                """.format(name, "About Me page", link)
            message = 'Subject: {}\n\n{}'.format(subject, mail_message)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(dustin_email, dustin_pw)
            server.sendmail(dustin_email, email, message)

        flash("The About Me page has been updated!")
        return redirect(url_for('auth.dash_about_me'))

    edit_form.welcome.data = about_edit.welcome
    edit_form.about.data = about_edit.about
    return render_template('dash_about_edit.html', title=title, about_edit=about_edit, edit_form=edit_form)


@auth.route('/delete-about', methods=['POST'])
def delete_about():
    about_del = json.loads(request.data)
    aboutId = about_del['aboutId']
    about_del = AboutMe.query.get(aboutId)
    if about_del:
        db.session.delete(about_del)
        db.session.commit()

    else:
        flash('This does not exist in database.', category='error')

    return jsonify({})


@auth.route('/delete-profpic', methods=['POST'])
def delete_profpic():
    profpic_del = json.loads(request.data)
    profpicId = profpic_del['profpicId']
    profpic_del = ProfilePic.query.get(profpicId)
    if profpic_del:
        db.session.delete(profpic_del)
        db.session.commit()

    else:
        flash('This Profile Picture does not exist in database.', category='error')

    return jsonify({})


# Sermons

@auth.route('/dash-sermons', methods=['GET', 'POST'])
@login_required
def dash_sermons():
    title = "Dash Sermons"
    sermon_list = Sermons.query.order_by(desc(Sermons.id))
    return render_template('dash_sermons.html', title=title, sermon_list=sermon_list)


@auth.route('/dash-sermons/<int:id>')
@login_required
def dash_sermon(id):
    sermon = Sermons.query.get_or_404(id)
    sermon_list = Sermons.query.order_by(Sermons.id)
    return render_template('dash_sermon.html', sermon=sermon, sermon_list=sermon_list)


@auth.route('/delete-sermon', methods=['POST'])
def delete_sermon():
    sermon_del = json.loads(request.data)
    sermonsId = sermon_del['sermonsId']
    sermon_del = Sermons.query.get(sermonsId)
    if sermon_del:
        db.session.delete(sermon_del)
        db.session.commit()

    else:
        flash('Blog does not exist in database.', category='error')

    return jsonify({})


# Blog

@auth.route('/dash-blog', methods=['GET', 'POST'])
@login_required
def dash_blog():
    title = "Dash Blog"
    blog_list = Blog.query.order_by(desc(Blog.id))
    return render_template('dash_blog.html', title=title, blog_list=blog_list)


@auth.route('/dash-blog/<int:id>')
@login_required
def dash_individual_blog(id):
    blog = Blog.query.get_or_404(id)
    return render_template('dash_individual_blog.html', blog=blog)


@auth.route('/dash-blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def dash_edit_blog(id):
    title = "Dash Blog Editor"
    blog = Blog.query.get_or_404(id)
    edit_form = BlogForm()
    if edit_form.validate_on_submit():
        blog.title = edit_form.title.data
        blog.content = edit_form.content.data
        # Update Database
        db.session.add(blog)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('auth.dash_blog'))
    edit_form.title.data = blog.title
    edit_form.content.data = blog.content
    return render_template('dash_edit_blog.html', title=title, edit_form=edit_form)


@auth.route('/delete-blog', methods=['POST'])
def delete_blog():
    blog_del = json.loads(request.data)
    blogId = blog_del['blogId']
    blog_del = Blog.query.get(blogId)
    if blog_del:
        db.session.delete(blog_del)
        db.session.commit()

    else:
        flash('Blog does not exist in database.', category='error')

    return jsonify({})


# Images

@auth.route('/dash-images', methods=['GET', 'POST'])
@login_required
def dash_images():
    title = "Dash Images"
    image_list = Pic.query.order_by(desc(Pic.id))
    return render_template('dash_images.html', title=title, image_list=image_list)


@auth.route('/delete-images', methods=['POST'])
def delete_images():
    images_del = json.loads(request.data)
    imagesId = images_del['imagesId']
    images_del = Pic.query.get(imagesId)
    if images_del:
        db.session.delete(images_del)
        db.session.commit()

    else:
        flash('Blog does not exist in database.', category='error')

    return jsonify({})


# Subscribers

@auth.route('/dash-subscribers', methods=['GET', 'POST'])
@login_required
def dash_subscribers():
    title = "Dash Subscribers"
    subscriber_list = Subscribers.query.order_by(Subscribers.id)
    return render_template('dash_subscribers.html', title=title, subscriber_list=subscriber_list)


@auth.route('/delete-subscribers', methods=['POST'])
def delete_subscribers():
    sub = json.loads(request.data)
    subscribersId = sub['subscribersId']
    sub = Subscribers.query.get(subscribersId)
    if sub:
        db.session.delete(sub)
        db.session.commit()

    else:
        flash('Subscriber does not exist in database.', category='error')

    return jsonify({})


@auth.route('/unsubscribe', methods=['POST', 'GET'])
def unsubscribe():
    sub = json.loads(request.data)
    subscribersId = sub['subscribersId']
    sub = Subscribers.query.get(subscribersId)
    if sub:
        db.session.delete(sub)
        db.session.commit()
        render_template('unsubscribe.html')
    else:
        flash('Subscriber does not exist in database.', category='error')

    return jsonify({})
