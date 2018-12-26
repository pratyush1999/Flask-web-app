from flask import render_template, Blueprint
from flask_login import current_user,login_required
from app.posts.forms import  PostForm, EditPostForm
from flask import  flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
import os
import secrets
from app.models import User, Post
from app import db
posts = Blueprint('posts', __name__)
    
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('post has been created')
        return redirect(url_for('users.user', username=current_user.username))
    return render_template('create_post.html', form=form, title='New Post')
@posts.route("/post/update/<int:post_id>", methods=['GET', 'POST'])
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
        return redirect(url_for('users.user', username=current_user.username))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html',title=post.title, post=post, form=form)
@posts.route("/post/delete/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted')
    return redirect(url_for('main.index'))
