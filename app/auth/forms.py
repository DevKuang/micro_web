#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Email,Length,Regexp,EqualTo,DataRequired
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email=StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField(u'密码',validators=[DataRequired()])
    remember_me=BooleanField(u'记住密码')
    submit=SubmitField(u'登录')

class RegistrationForm(FlaskForm):
    email=StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField(u'用户名',validators=[DataRequired(),Length(1,64)])
    password=PasswordField(u'密码',validators=[Required(),EqualTo('password2',message='Password must match.')])
    password2=PasswordField(u'确认密码',validators=[Required()])
    submit=SubmitField(u'注册')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已经存在！')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被占用！')

class ChangePasswordForm(FlaskForm):
    old_password=PasswordField(u'旧密码',validators=[Required()])
    password=PasswordField(u'新密码',validators=[Required(),EqualTo('password2',message='psw must match')])
    password2=PasswordField(u'确认密码',validators=[Required()])
    submit=SubmitField(u'修改密码')

class PasswordResetRequestForm(FlaskForm):
    email=StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
    submit=SubmitField(u'重置密码')

class PasswordResetForm(FlaskForm):
    email=StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
    password=PasswordField(u'新密码',validators=[Required(),EqualTo('password2',message='Password must be match')])
    password2=PasswordField(u'确认密码',validators=[Required()])
    submit=SubmitField(u'重置密码')

    def validate_emial(self,field):
        if User.query.filter_by(emial=field.data).first() is None:
            raise  ValidationError(u'未知邮件地址')



