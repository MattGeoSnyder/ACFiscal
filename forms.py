from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired

class ACH_Credits_Form(FlaskForm):
    file = FileField('ACH Credits (must be .csv file)',validators=[InputRequired()])

class ROC_Form(FlaskForm):
    roc = FileField('ROC (must be .xlsm or .pdf)',validators=[InputRequired()])
    supporting_docs = FileField('Supporting Documentation (must be .xlsm or .pdf)')