#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, current_app,flash,request,abort,\
    make_response
from flask_login import login_required,current_user
from . import main
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CreatePostForm,PostClassification,CommentForm
from ..models import User,Role,Permission,Post,Comment
from ..decorators import admin_required,permission_required
from .. import db

@main.route('/',methods=['POST','GET'])
def index():
    page=request.args.get('page',1,type=int)
    show_followed=False
    if current_user.is_authenticated:
        show_followed=bool(request.cookies.get('show_followed',''))
    if show_followed:
        query=current_user.followed_posts
    else:
        query=Post.query
    pagination=query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False
    )
    posts=pagination.items

    return render_template('index.html',posts=posts,show_followed=show_followed,
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash(u'你已经成功更改资料')
        return redirect(url_for('.user',username=current_user))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)


@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user=user) #?
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

#文章的固定地址
@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form=CommentForm()
    if form.validate_on_submit():
        comment=Comment(body=form.body.data,post=post,author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'已经成功提交评论')
        return redirect(url_for('.post',id=post.id,page=-1))
    page=request.args.get('page',1,type=int)
    if page==-1:
        page=(post.comments.count()-1)//\
            current_app.config['BLOG_COMMENTS_PER_PAGE']+1
    pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['BLOG_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments=pagination.items
    return render_template('post.html',posts=[post],form=form,
                           comments=comments,pagination=pagination)




@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = CreatePostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.classification=PostClassification.query.get(form.postclassification.data)
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.index'))
    form.body.data = post.body
    form.title.data=post.title
    form.postclassification.data=post.classification_id ####
    return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注该用户了')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash(u'你已经成功关注该用户')
    return redirect(url_for('.user',username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'该用户不存在')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你已经取消关注了该用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你已经成功取消关注 %s .' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followers.paginate(
        page,per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows=[{'user':item.follower,'timestamp':item.timestamp}
              for item in pagination.items]
    return render_template('followers.html',user=user,title="Followers of",
                           endpiont='.followers',pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u'该用户不存在')
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed.paginate(
        page,per_page=current_app.config['BLOG_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows=[{'user':item.followed,'timestamp':item.timestamp}
             for item in pagination.items]
    return  render_template('followers.html',user=user,title="Followed by",
                            endpiont='.followed_by',pagination=pagination,
                            follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/flask-post')
def flask_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(classification_id=1).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('post-classification.html',  posts=posts,
                           pagination=pagination)


@main.route('/flask-post-class/<int:id>')
def flask_post_class(id):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(classification_id=id).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('post-classification.html',  posts=posts,
                           pagination=pagination)



@main.route('/python-post')
def python_post():
    pass

@main.route('/book')
def book():
    pass

@main.route('/essays')
def essays():
    pass

@main.route('/ask-and-answer')
def ask_and_answer():
    pass

@main.route('/create-post',methods=['GET','POST'])
@login_required
def create_post():
    form=CreatePostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post=Post(title=form.title.data,body=form.body.data,classification=PostClassification.query.get(form.postclassification.data),\
                  author=current_user._get_current_object())
        db.session.add(post)
        flash(u'文章已经成功提交！')
        return redirect(url_for('.index'))
    return render_template('create_post.html',form=form)
    # form=PostForm()
    # return  render_template('create_post.html',form=form)