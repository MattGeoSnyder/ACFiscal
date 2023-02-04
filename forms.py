from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms.validators import InputRequired

class ACH_Credits(FlaskForm):
    ACH_Credits = FileField('ACH Credits (must be .csv file)', validators=[InputRequired()])