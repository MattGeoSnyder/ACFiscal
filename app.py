from flask import Flask, render_template, redirect, flash, request
from forms import ACH_Credits
from secret import app_secret_key
from flask_debugtoolbar import DebugToolbarExtension
from ach import process_ach
import os
import pdb



app = Flask(__name__)

app.config['SECRET_KEY'] = app_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ACFiscal'

toolbar = DebugToolbarExtension(app)

@app.route('/')
def go_to_fiscal(): 
    return redirect('/fiscal')

@app.route('/fiscal')
def get_homepage():
    return render_template('home.html')

@app.route('/fiscal/ACH')
def list_ach_credits():
    return render_template('ACH.html')

@app.route('/fiscal/ACH/add', methods = ['GET', 'POST'])
def add_ach_credits():
    form = ACH_Credits()
    if form.validate_on_submit():
        file_data = form.file.data
        filename = file_data.filename
        file_data.save(os.path.join(app.instance_path, 'ACH', 'ACHReport.csv'))
        process_ach(filename)
        return redirect('/fiscal/ACH')
            
    return render_template('ACH-add.html', form=form)
    


