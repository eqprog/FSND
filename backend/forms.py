from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL


class ThreadForm(FlaskForm):
    title = StringField(
        'title', validators=[DataRequired()]
    )
    content = TextAreaField(
        'content', validators=[DataRequired()]
    )