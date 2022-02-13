from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField
from wtforms.validators import DataRequired, URL,Email, NumberRange
from flask_ckeditor import CKEditorField



class Register_user(FlaskForm):
    email=StringField('EMAIL', validators=[Email(), DataRequired()])
    password = StringField("PASSWORD",validators=[DataRequired()])
    name=StringField("NAME",validators=[DataRequired()])
    submit = SubmitField("Register Me")

class Login(FlaskForm):
    email = StringField('EMAIL', validators=[Email(), DataRequired()])
    password = StringField("PASSWORD", validators=[DataRequired()])
    submit = SubmitField("Let Me In")

class Item(FlaskForm):
  product_name=StringField("NAME",validators=[DataRequired()])
  subtitle = StringField("Subtitle", validators=[DataRequired()])
  img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
  price = IntegerField('price $',validators=[DataRequired()])
  submit = SubmitField("Submit")

