from flask import Flask, render_template, redirect, flash, request
from forms import ACH_Credits_Form, ROC_Form
from secret import app_secret_key
from flask_debugtoolbar import DebugToolbarExtension
from ach import process_ach
from models import db, connect_db, ACH, ROC
import os
import pdb
import datetime



app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = app_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ACFiscal'
# app.config['SQLALCHEMY_ECHO'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

with app.app_context():
    # db.drop_all()
    db.create_all()

@app.route('/')
def go_to_fiscal(): 
    return redirect('/fiscal')

@app.route('/fiscal')
def get_homepage():
    return render_template('base.html')

@app.route('/fiscal/ACH')
def list_ach_credits():
    all_ach_credits = ACH.query.filter(ACH.claimed == None).order_by(ACH.received, ACH.amount, ACH.department).all()
    return render_template('ACH.html', ach_credits = all_ach_credits)

@app.route('/fiscal/ACH/claim', methods=['POST'])
def claim_ach_credits():
    form = ROC_Form()
    claimed_credits = request.form.getlist('credit-id')
    credit_ids = [ int(credit) for credit in claimed_credits ]
    ach_credits = ACH.query.filter(ACH.id.in_(credit_ids)).all()

    if form.validate_on_submit():
        # need to send credit ids with form on ACH-claim as well 
        pdb.set_trace()
        for credit in ach_credits:
            credit.claimed = datetime.today()
            print(credit)

        roc = form.roc.data.read()
        roc_filename = form.roc.data.filename
        roc = ROC(roc=roc, filename=roc_filename)
        db.session.add(roc)

        if form.supporting_docs.data:
            doc_data = form.supporting_docs.data.read()
            doc_name = form.supporting_docs.data.filename
            doc = SupportingDoc(doc=doc_data, filename=doc_name)
            db.session.add(doc)

        db.session.commit()    
        return redirect('/fiscal/ACH')

    total = 0
    for credit in ach_credits:
        total += credit.amount

    return render_template('ACH-claim.html', form=form, ach_credits=ach_credits,total=total)


@app.route('/fiscal/ACH/add', methods=['GET', 'POST'])
def add_ach_credits():
    form = ACH_Credits_Form()
    if form.validate_on_submit():
        file_data = form.file.data
        filename = file_data.filename
        file_data.save(os.path.join(app.instance_path, 'ACH', 'ACHReport.csv'))
        process_ach(filename)
        return redirect('/fiscal/ACH')
            
    return render_template('ACH-add.html', form=form)
    


