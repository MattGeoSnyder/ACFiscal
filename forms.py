from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import MultipleFileField, StringField, PasswordField, SelectField, DateField, FloatField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Regexp, Email

class PasswordValidator(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if form.password.data != form.confirm_password.data:
            raise ValidationError(self.message)    


class ACH_Credits_Form(FlaskForm):
    file = FileField('ACH Credits (must be .csv file)',validators=[InputRequired()])

class ROC_Form(FlaskForm):
    roc = FileField('ROC (must be .xlsm or .pdf)',validators=[InputRequired()])
    supporting_docs = MultipleFileField('Supporting Documentation (must be .xlsm or .pdf)')

class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Allegheny County E-mail', validators=[DataRequired(),
                                                                Regexp('[\w\.]+@alleghenycounty\.us$', message="You must sign up with your Allegheny County e-mail")
                                                            ])
    password = PasswordField('Password', validators=[DataRequired(), PasswordValidator(message='Passwords do not match')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), PasswordValidator(message='Passwords do not match')])
    department = SelectField('Department', coerce=int)

class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')

class UnclaimedCredits(FlaskForm):
    rec_start_date = DateField('Start Date')
    rec_end_date = DateField('End Date')
    department = SelectField('Department')
    bank = SelectField('Bank', choices=[('', 'All'),
                                        ('11151', '11151'),
                                        ('11102', '11102'),
                                        ('11103', '11103'), 
                                        ('11104', '11104'),
                                        ('11106', '11106'),
                                        ('11108', '11108')])
    amount = FloatField('Amount')
    
class AllCredits(UnclaimedCredits):
    clm_start_date = DateField('Start Date')
    clm_end_date = DateField('End Date')
    book_start_date = DateField('Start Date')
    book_end_date = DateField('End Date')
    