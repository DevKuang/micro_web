#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role,User,PostClassification


class NameForm(FlaskForm):
    name = StringField(u'你的名字是什么?', validators=[DataRequired()])
    submit = SubmitField(u'提交')


class EditProfileForm(FlaskForm):
    name=StringField(u'真实姓名',validators=[Length(0,64)])
    location=StringField(u'住址',validators=[Length(0,64)])
    about_me=TextAreaField(u'个人资料')
    submit=SubmitField(u'提交')


class EditProfileAdminForm(FlaskForm):
    email=StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField(u'用户名',validators=[DataRequired(),Length(1,64)])
    confirmed=BooleanField(u'邮箱是否验证')
    role=SelectField(u'角色',coerce=int)
    name=StringField(u'真实姓名',validators=[Length(0,64)])
    location=StringField(u'位置',validators=[Length(0,64)])
    about_me=StringField(u'关于我')
    submit=SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data!=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被占用')

    def validate_username(self,field):
        if field.data!=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被占用')


class PostForm(FlaskForm):
    title=StringField(u'标题',validators=[DataRequired()])
    body=PageDownField(u'内容')
    submit=SubmitField(u'提交')


class CreatePostForm(FlaskForm):
    postclassification=SelectField(u'文章类别',coerce=int)
    title=StringField(u'标题',validators=[DataRequired()])
    body=PageDownField(u'内容(支持Markdown)')
    submit=SubmitField(u'提交文章')

    def __init__(self,*args,**kwargs):
        super(CreatePostForm, self).__init__(*args,**kwargs)
        self.postclassification.choices=[(postclassification.id,postclassification.name)
                                     for postclassification in PostClassification.query.order_by(PostClassification.name).all()]


class CommentForm(FlaskForm):
    body=StringField(u'输入你的评论',validators=[DataRequired()])
    submit=SubmitField(u'提交')