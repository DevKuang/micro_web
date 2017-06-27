#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Email,Length,Regexp,EqualTo,DataRequired
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember_me=BooleanField('Keep me logged in')
    submit=SubmitField('Log in')

class RegistrationForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField('Username',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z0-9_.]*$',
                                                                              0,'Username must have onlyletters,'
                                                                              'numbers,dots or underscors')])
    password=PasswordField('Password',validators=[Required(),EqualTo('password2',message='Password must match.')])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangePasswordForm(FlaskForm):
    old_password=PasswordField('Old-Password',validators=[Required()])
    password=PasswordField('New password',validators=[Required(),EqualTo('password2',message='psw must match')])
    password2=PasswordField('Confirm your password',validators=[Required()])
    submit=SubmitField('Change Password')

class PasswordResetRequestForm(FlaskForm):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    submit=SubmitField('Reset Password')

class PasswordResetForm(FlaskForm):
    email=StringField('Email',validators=[Required(),Length(1,64),Email()])
    password=PasswordField('New Password',validators=[Required(),EqualTo('password2',message='Password must be match')])
    password2=PasswordField('Confirm password',validators=[Required()])
    submit=SubmitField('Reset Password')

    def validate_emial(self,field):
        if User.query.filter_by(emial=field.data).first() is None:
            raise  ValidationError('Unknown email address.')



