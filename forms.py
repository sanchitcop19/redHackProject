from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class SearchForm(FlaskForm):
    search = StringField(
        'Search', validators=[DataRequired()]
    )
    submit = SubmitField(
        'Submit'
    )
