from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
import os
import secrets

from app import app

from app import db

from app.forms import RegistrationForm, LoginForm, EditProfileForm, PostForm, EditPostForm
from flask_login import current_user, login_user, logout_user, login_required

from app.models import User, Post
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = {'username':'Miguel'}
	posts = [ ]
 #        {
 #            'author': {'username': 'John'},
 #            'body': 'Beautiful day in Portland!'
 #        },
 #        {
 #            'author': {'username': 'Susan'},
 #            'body': 'The Avengers movie was so cool!'
 #        }
 #    ]
    # posts=[]
	return render_template('index.html', title='Home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.all()
    image_file=url_for('static',filename=user.image_file)
    return render_template('user.html', user=user, posts=posts, image_file=image_file)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit() 

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.split(form_picture.filename)
    picture_fn = 'profile_pics/' + random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You have unfollowed {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('post has been created')
        return redirect(url_for('user', username=current_user.username))
    return render_template('create_post.html', form=form, title='New Post')
@app.route("/post/update/<int:post_id>", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm(post)
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data    
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html',title=post.title, post=post, form=form)
@app.route("/post/delete/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted')
    return redirect(url_for('index'))