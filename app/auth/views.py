#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user


from . import auth
from .. import db
from ..models import User
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,PasswordResetRequestForm,PasswordResetForm
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'无效密码')

    return render_template('auth/login.html',form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'退出成功')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,'Confirm Your Account',
                   'auth/email/confirm',user=user,token=token)
        flash(u'确认邮件已经发送到您的邮箱！')
        return redirect(url_for('auth.login'))
    return  render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'你已经成功确认了账户！')
    else:
        flash(u'该链接已经过期！')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
    flash(u'请到您的邮箱确认账户')
    return redirect(url_for('main.index'))


@auth.route('/change-password',methods=['POST','GET'])
@login_required
def change_password():
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            flash(u'你已经成功改变密码')
            return redirect(url_for('main.index'))
        else:
            flash('invalidate password')
    return render_template("auth/change_password.html",form=form)


@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=PasswordResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            token=user.generate_resret_token()
            send_email(user.email,'Reset Your Password',
                       'auth/email/reset_password',
                       user=user,token=token,
                       next=request.args.get('next'))#get next?
        flash(u'重置密码的邮件已经发送到您的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)


@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=PasswordResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash(u'你已经成功重置密码！')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)





