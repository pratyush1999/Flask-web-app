from flask import Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app.users.forms import RegistrationForm, LoginForm, EditProfileForm, MessageForm
from flask import  render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
import os
import secrets
from app.users.utils import save_picture
from app.models import User, Post, Message
from app import db
users = Blueprint('users', __name__)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('users.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
        
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)
@users.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.all()
    image_file=url_for('static',filename=user.image_file)
    return render_template('user.html', user=user, posts=posts, image_file=image_file)
@users.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('users.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
@users.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('users.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('users.user', username=username))

@users.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('users.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You have unfollowed {}.'.format(username))
    return redirect(url_for('users.user', username=username))

@users.route('/all_users')
@login_required
def all_users():
    users = User.query.all()
    return render_template('all_users.html', users=users)

@users.route('/message/<username>', methods=['GET', 'POST'])
@login_required
def message(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(content=form.content.data, reciever_id=user.id, sender_id=current_user.id)
        db.session.add(message)
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('users.all_users'))
    messages1=Message.query.filter_by(sender_id=user.id).filter_by(reciever_id=current_user.id)
    messages2=Message.query.filter_by(sender_id=current_user.id).filter_by(reciever_id=user.id)
    messages=messages1.union(messages2).all()
    for temp_message in messages:
        temp_message.sender_id=User.query.filter_by(id= temp_message.sender_id).first().username
    return render_template('message.html',form=form,messages=messages)