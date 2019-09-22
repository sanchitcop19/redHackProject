from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class SearchForm(Form):
    search = StringField(
        'Search', validators=[DataRequired()]
    )
    submit = SubmitField(
        'Submit'
    )
