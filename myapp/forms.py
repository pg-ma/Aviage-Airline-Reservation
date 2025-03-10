from flask import Flask, render_template
from .models import *
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email, ValidationError



class SignupForm(FlaskForm):
    FirstName = StringField("First Name", validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "First Name"})
    LastName = StringField("Last Name", validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Last Name"})
    
    email = StringField("Email", validators=[InputRequired(), Length(min=11, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Signup")
    
    def validate_username(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'That email already exists. Please choose a different one.')
            
class SigninForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(min=11, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Signin")