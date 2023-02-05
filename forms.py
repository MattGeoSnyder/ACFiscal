from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired

class ACH_Credits(FlaskForm):
    file = FileField('ACH Credits (must be .csv file)')